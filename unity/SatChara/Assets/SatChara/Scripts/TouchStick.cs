using System;
using UnityEngine;
using UnityEngine.EventSystems;

namespace SatChara
{
    public sealed class TouchStick : MonoBehaviour, IPointerDownHandler, IDragHandler, IPointerUpHandler
    {
        public Vector2 Value { get; private set; }
        public bool Held { get; private set; }
        public Action Released;
        public RectTransform Knob;
        private int pointer;
        public void OnPointerDown(PointerEventData data)
        {
            if (Held) return;
            Held = true; pointer = data.pointerId; OnDrag(data);
        }
        public void OnDrag(PointerEventData data)
        {
            if (!Held || data.pointerId != pointer) return;
            var rect = (RectTransform)transform;
            RectTransformUtility.ScreenPointToLocalPointInRectangle(rect, data.position, data.pressEventCamera, out var point);
            Value = Vector2.ClampMagnitude(point / (rect.rect.width * .4f), 1);
            if (Knob) Knob.anchoredPosition = Value * rect.rect.width * .28f;
        }
        public void OnPointerUp(PointerEventData data)
        {
            if (!Held || data.pointerId != pointer) return;
            bool used = Value.sqrMagnitude > .04f;
            ResetInput();
            if (used) Released?.Invoke();
        }
        public void ResetInput()
        {
            Held = false; Value = Vector2.zero;
            if (Knob) Knob.anchoredPosition = Vector2.zero;
        }
        private void OnDisable() => ResetInput();
    }
}
