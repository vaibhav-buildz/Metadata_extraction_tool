import { NextResponse } from 'next/server';

export async function POST(request) {
  try {
    const formData = await request.formData();
    
    // Attempt to hit the extract endpoint first
    let response = await fetch(
      'http://127.0.0.1:8000/api/extract',
      {
        method: 'POST',
        body: formData,
      }
    );

    // Fallback to analyze if extract is a 404
    if (response.status === 404) {
      response = await fetch(
        'http://127.0.0.1:8000/api/analyze',
        {
          method: 'POST',
          body: formData,
        }
      );
    }

    if (!response.ok) {
      return NextResponse.json(
        { error: `Backend returned ${response.status}: ${response.statusText}` },
        { status: response.status }
      );
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('API Route Error:', error);
    return NextResponse.json(
      { error: 'Failed to extract metadata in proxy' },
      { status: 500 }
    );
  }
}
