# AI Prompts (Gemini)

This document outlines the prompts used with the Google Gemini API (`gemini-1.5-flash-latest` model unless otherwise specified) via the `src/gemini_utils.py` module.

## 1. Generate Image Prompt (`generate_image_prompt`)

This prompt guides the LLM to create a detailed image generation prompt based on a Stoic quote.

**Current Active Prompt:**

```text
Based on the Stoic quote: '{quote_text}', craft an evocative image prompt (max 100 words) for an AI image generator.

1.  **Scene & Subject:** Describe a scene vividly capturing the quote's essence. Detail the main subject (this could be a person, animal, object, or even an abstract representation) and their action reflecting a Stoic principle (like acceptance, resilience, focus). Ensure the subject and scene are directly inspired by the quote and offer variety, not limited to classical figures or statues.
2.  **Setting & Atmosphere:** Paint a picture of the setting, specifying its atmosphere (e.g., a quiet natural landscape during twilight, a single focused individual amidst chaos, a simple room bathed in morning light).
3.  **Visual Style:** Define a clear visual style. Aim for a **cinematic and atmospheric quality**, often utilizing **dramatic, focused, or chiaroscuro-style lighting**. Styles like **realistic digital painting, atmospheric 3D render, high-detail illustration, or even stylized photorealism** fit well, but select the most appropriate for the specific quote.
4.  **Color Palette:** Specify a fitting color palette. Often lean towards **muted, deep, or contemplative tones (e.g., blues, grays, greens, earthy browns)**, but ensure it complements the scene's specific mood and subject.
5.  **Mood:** Convey the overall mood clearly (e.g., contemplative, resilient, tranquil acceptance, quiet determination).
6.  **Symbolism:** Include subtle, integrated symbolism related to the quote's core message.

Ensure the final output is *only* the image prompt itself, ready for an image generation model.
```

### Tested Variations (April 2025)

The following variations were tested using `src/test_image_prompt.py`. The "Original" prompt above was chosen as the active prompt.

**Variation 1 (Concise & Direct):**

```text
Create a visually striking image prompt (max 100 words) for an AI generator based on the Stoic quote: '{quote_text}'. The prompt must evoke Stoic philosophy and clearly define:
1. Subject/Action embodying a core principle from the quote.
2. Setting reinforcing the theme.
3. Specific Art Style (e.g., photorealistic, oil painting, minimalist illustration).
4. Mood & Color Palette (e.g., serene blues, determined earth tones).
5. Key Symbolism derived from the quote.
Output *only* the image prompt.
```

**Variation 2 (Technical Parameters):**

```text
Generate a detailed image prompt (max 100 words) for an AI generator from the Stoic quote: '{quote_text}'. Focus on philosophical depth and visual clarity. Specify:
*   Subject & Action: Central figure/element embodying a quote principle (posture, expression).
*   Setting: Contextual background (specific elements, atmosphere).
*   Visual Style: Precise artistic style (e.g., 'Cinematic photorealism', 'Classical oil painting', 'Stylized graphic art').
*   Color Palette: Mood-enhancing colors (e.g., 'Muted earth tones', 'Monochromatic grayscale', 'Sunrise hues').
*   Mood/Atmosphere: Desired tone (e.g., 'Stoic serenity', 'Quiet determination').
*   Symbolism: Relevant Stoic symbols from the quote.
*   Composition & Lighting: Framing and light (e.g., 'Centered, chiaroscuro', 'Rule of thirds, golden hour').
*   Parameters: Include '--ar 16:9 --style raw'. Add '--no text, words, signature' if appropriate.
Output *only* the image prompt itself.
```

**Variation 3 (Narrative Style):**

```text
Based on the Stoic quote: '{quote_text}', craft an evocative image prompt (max 100 words) for an AI generator. Describe a scene capturing the quote's essence. Detail the main subject and their action reflecting a Stoic principle. Paint a picture of the setting, specifying its atmosphere. Define a clear visual style (like photorealistic, illustration, or painting) and a fitting color palette. Convey the overall mood (e.g., contemplative, resilient). Include subtle symbolism related to the quote. Ensure the final output is *only* the image prompt.
```

## 2. Generate Explanation (`generate_explanation`)

This prompt guides the LLM to create a concise, action-oriented explanation of a Stoic quote.

```text
For the Stoic quote: '{quote_text}', provide a brief (under 100 words) explanation focusing on how someone could apply this idea in their daily life. What's the key takeaway action?