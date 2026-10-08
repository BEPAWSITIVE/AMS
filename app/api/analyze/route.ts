import { NextResponse } from 'next/server';

export async function POST(req: Request) {
  try {
    const { images } = await req.json();
    
    if (!images || images.length === 0) {
      return NextResponse.json({ error: 'No images provided' }, { status: 400 });
    }

    const apiKey = process.env.GEMINI_API_KEY;
    if (!apiKey) {
      return NextResponse.json({ error: 'GEMINI_API_KEY is missing. Add it to Vercel env vars.' }, { status: 500 });
    }

    const parts = images.map((base64Data: string) => {
      const b64 = base64Data.replace(/^data:image\/\w+;base64,/, "");
      return {
        inlineData: {
          mimeType: "image/jpeg",
          data: b64
        }
      };
    });

    parts.push({
      text: `Analyze the provided image(s). Determine if it is a delivery package/parcel OR an ID document (Aadhaar, DL, Passport, Voter ID, ID Card, etc.).
Return ONLY a raw JSON object (no markdown formatting, no code blocks) with the following exact structure:

If it is a delivery parcel:
{"type": "parcel", "company_name": "Delivery company like Amazon, Flipkart, BlueDart, Swiggy", "recipient_name": "Name of person receiving it", "barcode": "Any tracking number or barcode text"}

If it is an ID document (for a visitor):
{"type": "visitor", "name": "Full name of the person", "id_number": "The ID number", "address": "Full address if visible"}

If it is completely unreadable or neither:
{"type": "unknown"}
`
    });

    const response = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=${apiKey}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        contents: [{ parts }],
        generationConfig: {
          temperature: 0.1,
          responseMimeType: "application/json"
        }
      })
    });

    const data = await response.json();
    
    if (data.error) {
      console.error("Gemini API Error:", data.error);
      return NextResponse.json({ error: data.error.message }, { status: 500 });
    }

    const textOutput = data.candidates[0].content.parts[0].text;
    const jsonStr = textOutput.replace(/```json/g, '').replace(/```/g, '').trim();
    const result = JSON.parse(jsonStr);

    return NextResponse.json(result);

  } catch (err: any) {
    console.error("Analyze error:", err);
    return NextResponse.json({ error: err.message }, { status: 500 });
  }
}
