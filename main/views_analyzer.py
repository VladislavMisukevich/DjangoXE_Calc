import base64
import json
import re
from typing import Dict, Any

from django.conf import settings
from django.shortcuts import render
from openai import OpenAI


def get_openai_client() -> OpenAI:
    return OpenAI(api_key=settings.OPENAI_API_KEY)


def normalize_result(data: Dict[str, Any]) -> Dict[str, Any]:
    macros = data.get("macros_per_100g") or {}
    carbs = macros.get("carbs_g")

    xe = round(carbs / 12, 2) if carbs else None

    return {
        "name": data.get("name"),
        "ingredients": data.get("ingredients") or [],
        "macros_per_100g": macros,
        "calories_per_100g": data.get("calories_per_100g"),
        "xe_per_100g": xe,
    }


def image_analyzer(request):
    if request.method == "POST" and request.FILES.get("image"):
        image_b64 = base64.b64encode(
            request.FILES["image"].read()
        ).decode()

        client = get_openai_client()

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Верни ТОЛЬКО JSON:\n"
                        "{name, ingredients, "
                        "macros_per_100g{protein_g,fat_g,carbs_g}, "
                        "calories_per_100g}"
                    ),
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_b64}"
                            },
                        }
                    ],
                },
            ],
            max_tokens=800,
        )

        raw = response.choices[0].message.content

        data = json.loads(
            re.search(r"\{.*\}", raw, re.S).group()
        )

        result = normalize_result(data)

        return render(
            request,
            "main/image_analyzer.html",
            {"result": result},
        )

    return render(request, "main/image_analyzer.html")
