import { Metadata } from 'next';
import Image from 'next/image';

type Props = {
  params: { id: string }
}

export async function generateMetadata(
  { params }: Props
): Promise<Metadata> {
  const imageUrl = `https://rcsjwdtatnqodekwqpur.supabase.co/storage/v1/object/public/qr-passes/${params.id}`;
  
  return {
    title: 'Your Attendance Pass',
    openGraph: {
      images: [imageUrl],
    },
  }
}

export default function PassPage({ params }: Props) {
  const imageUrl = `https://rcsjwdtatnqodekwqpur.supabase.co/storage/v1/object/public/qr-passes/${params.id}`;

  return (
    <div className="min-h-screen bg-[#F4F9FF] flex flex-col items-center justify-center p-4">
      <div className="max-w-md w-full bg-white rounded-3xl shadow-xl overflow-hidden p-6 flex flex-col items-center">
        
        <h1 className="text-xl font-bold text-gray-800 mb-6 text-center">Your Attendance Pass</h1>
        
        <div className="relative w-full aspect-[3/4] max-w-[300px] mb-8 rounded-2xl overflow-hidden shadow-md border border-gray-100">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img 
            src={imageUrl} 
            alt="QR Pass" 
            className="w-full h-full object-contain"
          />
        </div>

        <a 
          href={imageUrl} 
          download={`Attendance_Pass_${params.id}`}
          className="w-full max-w-[300px] bg-blue-600 hover:bg-blue-700 text-white font-bold py-4 px-6 rounded-xl text-center shadow-lg transition-colors flex items-center justify-center"
        >
          <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
          </svg>
          Download to Phone
        </a>
        
        <p className="text-xs text-gray-400 mt-6 text-center">
          Save this image to your phone's photo gallery and scan it at the entrance.
        </p>
      </div>
    </div>
  );
}
