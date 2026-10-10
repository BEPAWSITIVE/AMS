import { NextRequest, NextResponse } from 'next/server';

export const maxDuration = 30; // 30 seconds max for AI

export async function POST(req: NextRequest) {
  try {
    const { images, category } = await req.json();
    const apiKey = process.env.GEMINI_API_KEY;

    if (!apiKey) {
      return NextResponse.json({ error: 'AI is not configured. Missing API Key.' }, { status: 500 });
    }

    if (!images || images.length === 0) {
      return NextResponse.json({ error: 'No images provided.' }, { status: 400 });
    }

    // Convert base64 data URIs to raw base64
    const parts = images.map((img: string) => {
      const base64Data = img.split(',')[1] || img;
      return {
        inlineData: {
          data: base64Data,
          mimeType: "image/jpeg"
        }
      };
    });

    const promptText = `
    You are an AI assistant for a facility management system. The user uploaded a photo of a physical register or list of ${category} records.
    Your job is to read the document and extract ALL individuals/vehicles listed.
    
    If category is 'Vehicle', extract: name (driver or owner name), phone, id_number (vehicle plate), address (department or company).
    If category is 'Staff', 'Volunteer', or 'Workexchange', extract: name, phone, id_number (ID card or Aadhar), address (department, role, or location).
    
    Return EXACTLY a JSON array of objects. Do not wrap it in markdown block quotes like \`\`\`json. Return ONLY the raw JSON array.
    Format:
    [
      { "name": "...", "phone": "...", "id_number": "...", "address": "..." },
      ...
    ]
    
    If nothing is found, return an empty array [].
    `;

    parts.unshift({ text: promptText });

    const response = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=${apiKey}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        contents: [{ parts }],
        generationConfig: {
          temperature: 0.2,
        }
      })
    });

    if (!response.ok) {
      const errText = await response.text();
      return NextResponse.json({ error: `Gemini API Error: ${errText}` }, { status: response.status });
    }

    const data = await response.json();
    let text = data.candidates?.[0]?.content?.parts?.[0]?.text;

    if (!text) {
      return NextResponse.json({ error: 'AI returned an empty response.' }, { status: 500 });
    }

    // Clean up possible markdown wrappers
    text = text.replace(/```json/g, '').replace(/```/g, '').trim();

    const parsed = JSON.parse(text);

    return NextResponse.json({ records: parsed });
  } catch (err: any) {
    return NextResponse.json({ error: err.message }, { status: 500 });
  }
}
