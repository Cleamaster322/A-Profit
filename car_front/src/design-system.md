# Design system rules

## 1. Core style

- Use black / white palette with light gray background for page surfaces.
- Keep square corners: no border radius except subtle values in rare cases.
- Main panels and cards have a 2px black border and no shadow.
- Typography is bold and direct; headings are uppercase-free and visually heavy.

## 2. Buttons

- Primary actions use black background with white text.
- Secondary actions use white background with black border.
- All buttons keep `textTransform: none` and consistent height.

## 3. Form fields

- Text fields must use outlined variant.
- Input background stays white with square corners.
- Labels use black color and values stay medium-weight.

## 4. Panels and blocks

- Page shells: light gray backgrounds, 2px black border, padding-driven composition.
- Section cards: white surface, 2px black border, steady spacing between blocks.
- Detailed chips and pills use light gray backgrounds and black text.

## 5. Usage guidance

- Reuse shared constants from `theme.js` rather than creating ad hoc object styles in each file.
- Prefer `commonSx.page`, `commonSx.panel`, `commonSx.field`, `commonSx.primaryButton`, and `commonSx.secondaryButton`.
- Keep new CSS local only for one-off layout exceptions, not for the standard project design language.
