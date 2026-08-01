import json
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .models import SolveHistory
from . import vision
from .validators import validate_cube_state, FACE_ORDER


def capture(request):
    return render(request, 'solver/capture.html')


@csrf_exempt
@require_POST
def detect(request):
    try:
        data = json.loads(request.body)
        images = {face: data.get(face, '') for face in FACE_ORDER}
        colors = vision.get_all_face_colors(images)
        return JsonResponse({'colors': colors})
    except (ValueError, RuntimeError) as exc:
        return JsonResponse({'error': str(exc)}, status=422)
    except Exception as exc:
        return JsonResponse({'error': f'Unexpected error: {exc}'}, status=500)


@csrf_exempt
@require_POST
def detect_face(request):
    try:
        data = json.loads(request.body)
        face = data.get('face', '')
        image = data.get('image', '')
        if face not in FACE_ORDER:
            return JsonResponse({'error': f'Invalid face: {face}'}, status=400)
        if not image:
            return JsonResponse({'error': 'No image provided'}, status=400)
        colors = vision.get_single_face_colors(face, image)
        return JsonResponse({'colors': {face: colors}})
    except (ValueError, RuntimeError) as exc:
        return JsonResponse({'error': str(exc)}, status=422)
    except Exception as exc:
        return JsonResponse({'error': f'Unexpected error: {exc}'}, status=500)


@csrf_exempt
@require_POST
def solve(request):
    try:
        data = json.loads(request.body)
        colors = data.get('colors', {})
        validate_cube_state(colors)
        request.session['cube_colors'] = colors
        return JsonResponse({'status': 'ok'})
    except ValueError as exc:
        return JsonResponse({'error': str(exc)}, status=400)
    except Exception as exc:
        return JsonResponse({'error': f'Unexpected error: {exc}'}, status=500)


def solve_page(request):
    colors = request.session.get('cube_colors')
    if not colors:
        return redirect('capture')
    return render(request, 'solver/solve.html', {
        'colors_json': json.dumps(colors),
    })


@csrf_exempt
@require_POST
def save_solve(request):
    try:
        data = json.loads(request.body)
        SolveHistory.objects.create(
            colors=data.get('colors', {}),
            moves=data.get('moves', []),
            move_count=data.get('move_count', 0),
            solve_time_ms=data.get('solve_time_ms', 0),
        )
        return JsonResponse({'status': 'ok'})
    except Exception as exc:
        return JsonResponse({'error': str(exc)}, status=500)


def history(request):
    solves = SolveHistory.objects.all()[:50]
    return render(request, 'solver/history.html', {'solves': solves})
