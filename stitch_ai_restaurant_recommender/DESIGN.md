---
name: Epicurean Elite
colors:
  surface: '#f9f9f9'
  surface-dim: '#dadada'
  surface-bright: '#f9f9f9'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f3f3f3'
  surface-container: '#eeeeee'
  surface-container-high: '#e8e8e8'
  surface-container-highest: '#e2e2e2'
  on-surface: '#1a1c1c'
  on-surface-variant: '#5b403f'
  inverse-surface: '#2f3131'
  inverse-on-surface: '#f1f1f1'
  outline: '#8f6f6e'
  outline-variant: '#e4bebc'
  surface-tint: '#bb162c'
  primary: '#b7122a'
  on-primary: '#ffffff'
  primary-container: '#db313f'
  on-primary-container: '#fffbff'
  inverse-primary: '#ffb3b1'
  secondary: '#5f5e5e'
  on-secondary: '#ffffff'
  secondary-container: '#e2dfde'
  on-secondary-container: '#636262'
  tertiary: '#65595b'
  on-tertiary: '#ffffff'
  tertiary-container: '#7f7173'
  on-tertiary-container: '#fffbff'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#ffdad8'
  primary-fixed-dim: '#ffb3b1'
  on-primary-fixed: '#410007'
  on-primary-fixed-variant: '#92001c'
  secondary-fixed: '#e5e2e1'
  secondary-fixed-dim: '#c8c6c5'
  on-secondary-fixed: '#1b1b1b'
  on-secondary-fixed-variant: '#474746'
  tertiary-fixed: '#f0dee0'
  tertiary-fixed-dim: '#d3c3c5'
  on-tertiary-fixed: '#22191b'
  on-tertiary-fixed-variant: '#4f4446'
  background: '#f9f9f9'
  on-background: '#1a1c1c'
  surface-variant: '#e2e2e2'
  white: '#FFFFFF'
  success-green: '#24963F'
  rating-gold: '#FFBA00'
  border-subtle: '#E8E8E8'
  text-muted: '#696969'
typography:
  display-lg:
    fontFamily: metropolis
    fontSize: 48px
    fontWeight: '700'
    lineHeight: 56px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: metropolis
    fontSize: 32px
    fontWeight: '700'
    lineHeight: 40px
    letterSpacing: -0.01em
  headline-lg-mobile:
    fontFamily: metropolis
    fontSize: 24px
    fontWeight: '700'
    lineHeight: 32px
  headline-md:
    fontFamily: metropolis
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
  headline-sm:
    fontFamily: metropolis
    fontSize: 20px
    fontWeight: '600'
    lineHeight: 28px
  body-lg:
    fontFamily: metropolis
    fontSize: 18px
    fontWeight: '400'
    lineHeight: 28px
  body-md:
    fontFamily: metropolis
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  body-sm:
    fontFamily: metropolis
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  label-lg:
    fontFamily: metropolis
    fontSize: 14px
    fontWeight: '600'
    lineHeight: 20px
    letterSpacing: 0.01em
  label-sm:
    fontFamily: metropolis
    fontSize: 12px
    fontWeight: '500'
    lineHeight: 16px
    letterSpacing: 0.02em
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  unit: 4px
  xs: 4px
  sm: 8px
  md: 16px
  lg: 24px
  xl: 32px
  xxl: 48px
  container-max: 1200px
  gutter: 16px
---

## Brand & Style

The design system is engineered for a premium, high-velocity restaurant discovery experience. The brand personality is **confident, appetizing, and efficient**, catering to food enthusiasts who value both visual inspiration and functional speed.

The aesthetic follows a **Corporate Modern** approach with **Minimalist** influences. It prioritizes high-quality food photography by utilizing expansive white space and a restrained but punchy color palette. The UI is designed to feel like a high-end concierge: reliable, polished, and intuitive. Visual hierarchy is established through clear typographic scaling and intentional use of the signature primary red for high-intent actions.

## Colors

The color strategy centers on **Zomato Red (#E23744)** as the primary brand signal, reserved for critical conversion points like "Order Now," "Book Table," and primary navigation states. 

- **Primary:** High-energy red for actions and brand identity.
- **Secondary:** A deep, near-black neutral for primary text and heavy iconography to ensure maximum contrast.
- **Tertiary:** A soft, desaturated rose-tinted white used for card backgrounds or subtle highlight states (e.g., active filters).
- **Neutral:** A light gray background (#F8F8F8) provides a clean canvas that differentiates the page surface from white content cards.

Functional colors include a specific gold for ratings and a vibrant green for hygiene and availability indicators.

## Typography

This design system utilizes **Metropolis**, a geometric sans-serif that balances modern efficiency with approachability. 

- **Scale:** A tight, 4px-based typographic scale ensures readability across dense listing pages.
- **Hierarchy:** Headlines use Bold (700) or Semi-Bold (600) weights to anchor the eye. Body text stays strictly at Regular (400) for long-form menus or descriptions.
- **Mobile Adaptivity:** Larger headlines scale down on mobile to prevent awkward line breaks while maintaining visual impact.
- **Contrast:** Utilize `secondary_color_hex` for headings and `text-muted` for secondary labels or meta-information (e.g., timestamps, distances).

## Layout & Spacing

The layout employs a **12-column fixed grid** for desktop, centering content to maintain a premium feel. On mobile, it transitions to a single-column fluid layout with 16px side margins.

- **Rhythm:** An 8px spatial system governs all padding and margins. 
- **Cards:** Restaurant cards use a standard `md` (16px) internal padding.
- **Sections:** Large homepage sections are separated by `xxl` (48px) spacing to prevent visual clutter and give photography room to breathe.
- **Grids:** Restaurant listings should utilize a 3-column grid on desktop and a 1-column stack on mobile to maximize image height.

## Elevation & Depth

Visual depth is achieved through **Tonal Layers** combined with **Ambient Shadows**. 

- **Surface Levels:** The base layer is `neutral_color_hex` (#F8F8F8). Active content elements (Cards, Modals) reside on a pure white (#FFFFFF) surface.
- **Shadow Profile:** Shadows must be extremely subtle to maintain a "clean" look. Use a large blur radius (16px-24px) with very low opacity (4-6%) and a slight Y-axis offset.
- **Interaction:** On hover, cards should slightly lift (increase Y-offset and blur) to provide tactile feedback without looking heavy.
- **Overlays:** Full-screen modals use a 40% opacity black backdrop to focus the user on the task at hand.

## Shapes

The shape language is consistently **Rounded**, reflecting a friendly and consumer-focused identity.

- **Base Radius:** 0.5rem (8px) for small elements like buttons and input fields.
- **Large Radius:** 1rem (16px) for restaurant cards, image containers, and bottom sheets.
- **Pill Shapes:** Used exclusively for tags, chips, and search bars to differentiate them from actionable cards.
- **Consistency:** Never mix sharp corners with rounded ones; even image thumbnails must inherit the container's corner radius.

## Components

- **Buttons:** Primary buttons are solid `primary_color_hex` with white text. Secondary buttons use an outline of `border-subtle` with `secondary_color_hex` text.
- **Cards:** The core of the experience. Cards must have a white background, 16px corner radius, and a 1px `border-subtle` or a very soft ambient shadow. Images within cards must bleed to the top and sides.
- **Chips/Filters:** Pill-shaped with a light gray fill and 12px horizontal padding. Active states use a `primary_color_hex` border and light `tertiary_color_hex` fill.
- **Inputs:** Search bars should be pill-shaped with a 1px `border-subtle` and a magnifying glass icon. Focused inputs use a `primary_color_hex` border.
- **Ratings:** Displayed as a small rounded-sm badge. Use `success-green` for high ratings (4.0+) and `rating-gold` for mid-tier ratings.
- **Lists:** Menu items should be separated by a 1px horizontal line of `border-subtle` with ample vertical padding (16px) to maintain readability.