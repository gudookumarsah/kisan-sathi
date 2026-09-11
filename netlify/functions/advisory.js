// Kisan Sathi — advisory generator
// Calls Google Gemini's free tier (generativelanguage.googleapis.com).
// Requires an env var GEMINI_API_KEY set in Netlify's dashboard (Site settings > Environment variables).
// Get a free key (no credit card needed) at https://aistudio.google.com/apikey

exports.handler = async function (event) {
  if (event.httpMethod !== 'POST') {
    return { statusCode: 405, body: 'Method Not Allowed' };
  }

  let payload;
  try {
    payload = JSON.parse(event.body);
  } catch (e) {
    return { statusCode: 400, body: JSON.stringify({ error: 'invalid_json' }) };
  }

  const { cropLabel, homeMarketLabel, homePrice, othersText, tone } = payload;

  const toneInstruction = tone === 'local'
    ? 'भाषा शैली: तराई/मधेशको बोलचालको लवजमा, सरल र न्यानो शब्दमा लेख्नुहोस् (देवनागरी नेपाली लिपिमा नै)।'
    : 'भाषा शैली: मानक सामान्य नेपाली, स्पष्ट र सरल।';

  const prompt = `तपाईं एक कृषि बजार सल्लाहकार हुनुहुन्छ जसले नेपाल (तराई/मधेश क्षेत्र) का किसानहरूलाई तिनीहरूको उब्जनी कहाँ र कहिले बेच्ने भन्ने बारे छोटो, व्यावहारिक सल्लाह दिनुहुन्छ।

बाली: ${cropLabel}
किसानको नजिकको बजार: ${homeMarketLabel} — मूल्य: रु ${homePrice}/केजी
अन्य बजारहरूको मूल्य: ${othersText}

${toneInstruction}

माथिको जानकारीको आधारमा किसानलाई ३-४ वाक्यमा नेपालीमा (मार्कडाउन वा तारा चिन्ह नराखी, सादा वाक्य मात्र) व्यावहारिक सल्लाह दिनुहोस्: स्थानीय बजारमै बेच्ने कि टाढाको राम्रो मूल्य भएको बजार हेर्ने, ढुवानी खर्च विचार गर्दै। छिमेकीले सल्लाह दिए जस्तो सहज भाषामा लेख्नुहोस्।`;

  const apiKey = process.env.GEMINI_API_KEY;
  if (!apiKey) {
    return { statusCode: 500, body: JSON.stringify({ error: 'missing_api_key' }) };
  }

  const MODEL = 'gemini-2.5-flash';

  try {
    const res = await fetch(
      `https://generativelanguage.googleapis.com/v1beta/models/${MODEL}:generateContent?key=${apiKey}`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          contents: [{ parts: [{ text: prompt }] }],
        }),
      }
    );
    const data = await res.json();
    const text = data?.candidates?.[0]?.content?.parts?.[0]?.text?.trim();

    if (!text) {
      return { statusCode: 502, body: JSON.stringify({ error: 'no_text_returned', raw: data }) };
    }
    return { statusCode: 200, body: JSON.stringify({ text }) };
  } catch (err) {
    return { statusCode: 500, body: JSON.stringify({ error: 'gemini_request_failed' }) };
  }
};
