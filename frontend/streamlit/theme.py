"""Centralized Neon Enterprise UI Theme System.

This module defines the complete design system for the Banking Analytics Platform,
based on the reference UI screenshots featuring dark neon enterprise aesthetics.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Tuple


@dataclass
class NeonColors:
    """Neon color palette extracted from reference screenshots."""

    # Background colors - Near-black with teal atmospheric glow
    background_base: str = "#05070A"
    background_layer_1: str = "#080D12"
    background_layer_2: str = "#0A1117"
    background_layer_3: str = "#0D161D"

    # Panel colors - Dark glass panels
    panel_base: str = "#0C1218"
    panel_light: str = "#101820"
    panel_border: str = "#111A22"

    # Primary accent - Cyan for primary information/active state
    cyan: str = "#00F5FF"
    cyan_dim: str = "rgba(0, 245, 255, 0.1)"
    cyan_glow: str = "rgba(0, 245, 255, 0.3)"

    # Secondary accent - Purple/Magenta for AI/advanced analytics
    purple: str = "#9D00FF"
    purple_dim: str = "rgba(157, 0, 255, 0.1)"
    purple_glow: str = "rgba(157, 0, 255, 0.3)"

    magenta: str = "#FF00D4"
    magenta_dim: str = "rgba(255, 0, 212, 0.1)"
    magenta_glow: str = "rgba(255, 0, 212, 0.3)"

    # Status colors
    green: str = "#00FF9C"  # Success/healthy/growth
    green_dim: str = "rgba(0, 255, 156, 0.1)"
    green_glow: str = "rgba(0, 255, 156, 0.3)"

    orange: str = "#FF8A00"  # Warning/attention
    orange_dim: str = "rgba(255, 138, 0, 0.1)"
    orange_glow: str = "rgba(255, 138, 0, 0.3)"

    red: str = "#FF3158"  # Critical/anomaly/high risk
    red_dim: str = "rgba(255, 49, 88, 0.1)"
    red_glow: str = "rgba(255, 49, 88, 0.3)"

    yellow: str = "#FFE600"  # Important insights
    yellow_dim: str = "rgba(255, 230, 0, 0.1)"
    yellow_glow: str = "rgba(255, 230, 0, 0.3)"

    # Text colors
    white: str = "#F5FAFF"
    white_dim: str = "rgba(245, 250, 255, 0.7)"
    muted: str = "#82909D"
    muted_dim: str = "rgba(130, 144, 157, 0.5)"

    # Gradients
    gradient_cyan_purple: str = "linear-gradient(135deg, #00F5FF 0%, #9D00FF 100%)"
    gradient_purple_magenta: str = "linear-gradient(135deg, #9D00FF 0%, #FF00D4 100%)"
    gradient_tea_l: str = "linear-gradient(180deg, #05070A 0%, #0A1117 100%)"
    gradient_atmospheric: str = "radial-gradient(ellipse at top, rgba(0, 245, 255, 0.05) 0%, transparent 50%)"


@dataclass
class NeonTypography:
    """Typography system for neon enterprise UI."""

    # Font families
    font_family_base: str = "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"
    font_family_mono: str = "'JetBrains Mono', 'Fira Code', monospace"

    # Font sizes
    size_xs: str = "0.75rem"    # 12px
    size_sm: str = "0.875rem"   # 14px
    size_base: str = "1rem"     # 16px
    size_lg: str = "1.125rem"   # 18px
    size_xl: str = "1.25rem"    # 20px
    size_2xl: str = "1.5rem"    # 24px
    size_3xl: str = "1.875rem"  # 30px
    size_4xl: str = "2.25rem"   # 36px
    size_5xl: str = "3rem"      # 48px

    # Font weights
    weight_light: int = 300
    weight_normal: int = 400
    weight_medium: int = 500
    weight_semibold: int = 600
    weight_bold: int = 700
    weight_extrabold: int = 800

    # Line heights
    leading_tight: float = 1.25
    leading_normal: float = 1.5
    leading_relaxed: float = 1.75


@dataclass
class NeonSpacing:
    """Spacing system for consistent layout."""

    # Base unit
    unit: str = "0.25rem"  # 4px

    # Spacing scale
    space_0: str = "0"
    space_1: str = "0.25rem"   # 4px
    space_2: str = "0.5rem"    # 8px
    space_3: str = "0.75rem"   # 12px
    space_4: str = "1rem"      # 16px
    space_5: str = "1.25rem"   # 20px
    space_6: str = "1.5rem"    # 24px
    space_8: str = "2rem"      # 32px
    space_10: str = "2.5rem"   # 40px
    space_12: str = "3rem"     # 48px
    space_16: str = "4rem"     # 64px
    space_20: str = "5rem"     # 80px


@dataclass
class NeonBorders:
    """Border and radius system."""

    # Border radius
    radius_none: str = "0"
    radius_sm: str = "0.25rem"   # 4px
    radius_base: str = "0.5rem"  # 8px
    radius_lg: str = "0.75rem"   # 12px
    radius_xl: str = "1rem"     # 16px
    radius_2xl: str = "1.5rem"  # 24px
    radius_full: str = "9999px"

    # Border width
    width_none: str = "0"
    width_thin: str = "1px"
    width_base: str = "2px"
    width_thick: str = "3px"

    # Border styles
    style_solid: str = "solid"
    style_dashed: str = "dashed"
    style_dotted: str = "dotted"


@dataclass
class NeonShadows:
    """Shadow and glow system for neon effects."""

    # Subtle shadows
    shadow_sm: str = "0 1px 2px 0 rgba(0, 0, 0, 0.05)"
    shadow_base: str = "0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)"
    shadow_md: str = "0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)"
    shadow_lg: str = "0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)"

    # Neon glow effects
    glow_cyan: str = "0 0 20px rgba(0, 245, 255, 0.3), 0 0 40px rgba(0, 245, 255, 0.1)"
    glow_purple: str = "0 0 20px rgba(157, 0, 255, 0.3), 0 0 40px rgba(157, 0, 255, 0.1)"
    glow_green: str = "0 0 20px rgba(0, 255, 156, 0.3), 0 0 40px rgba(0, 255, 156, 0.1)"
    glow_orange: str = "0 0 20px rgba(255, 138, 0, 0.3), 0 0 40px rgba(255, 138, 0, 0.1)"
    glow_red: str = "0 0 20px rgba(255, 49, 88, 0.3), 0 0 40px rgba(255, 49, 88, 0.1)"

    # Panel glow
    panel_glow: str = "0 0 30px rgba(0, 0, 0, 0.3), inset 0 0 30px rgba(0, 0, 0, 0.1)"


@dataclass
class NeonAnimation:
    """Animation system for subtle professional effects."""

    # Duration
    duration_fast: str = "150ms"
    duration_base: str = "300ms"
    duration_slow: str = "500ms"
    duration_slower: str = "700ms"

    # Easing
    ease_linear: str = "linear"
    ease_in: str = "ease-in"
    ease_out: str = "ease-out"
    ease_in_out: str = "ease-in-out"
    ease_bounce: str = "cubic-bezier(0.68, -0.55, 0.265, 1.55)"

    # Keyframe animations
    fade_in: str = "fadeIn 0.6s ease-out"
    fade_in_down: str = "fadeInDown 0.6s ease-out"
    fade_in_up: str = "fadeInUp 0.6s ease-out"
    slide_in: str = "slideIn 0.5s ease-out"
    pulse_subtle: str = "pulse 3s ease-in-out infinite"
    glow_pulse: str = "glowPulse 2s ease-in-out infinite"


@dataclass
class NeonLayout:
    """Layout and responsive breakpoints."""

    # Container widths
    container_sm: str = "640px"
    container_md: str = "768px"
    container_lg: str = "1024px"
    container_xl: str = "1280px"
    container_2xl: str = "1536px"

    # Sidebar
    sidebar_width: str = "280px"
    sidebar_collapsed_width: str = "80px"

    # KPI cards
    kpi_card_height: str = "140px"
    kpi_card_min_width: str = "200px"

    # Charts
    chart_height_sm: str = "300px"
    chart_height_base: str = "400px"
    chart_height_lg: str = "500px"
    chart_height_xl: str = "600px"


@dataclass
class NeonTheme:
    """Complete neon enterprise theme configuration."""

    colors: NeonColors = field(default_factory=NeonColors)
    typography: NeonTypography = field(default_factory=NeonTypography)
    spacing: NeonSpacing = field(default_factory=NeonSpacing)
    borders: NeonBorders = field(default_factory=NeonBorders)
    shadows: NeonShadows = field(default_factory=NeonShadows)
    animation: NeonAnimation = field(default_factory=NeonAnimation)
    layout: NeonLayout = field(default_factory=NeonLayout)

    def get_css_variables(self) -> str:
        """Generate CSS custom properties for the theme."""
        return f"""
        :root {{
            /* Backgrounds */
            --bg-base: {self.colors.background_base};
            --bg-layer-1: {self.colors.background_layer_1};
            --bg-layer-2: {self.colors.background_layer_2};
            --bg-layer-3: {self.colors.background_layer_3};

            /* Panels */
            --panel-base: {self.colors.panel_base};
            --panel-light: {self.colors.panel_light};
            --panel-border: {self.colors.panel_border};

            /* Colors */
            --color-cyan: {self.colors.cyan};
            --color-cyan-dim: {self.colors.cyan_dim};
            --color-cyan-glow: {self.colors.cyan_glow};

            --color-purple: {self.colors.purple};
            --color-purple-dim: {self.colors.purple_dim};
            --color-purple-glow: {self.colors.purple_glow};

            --color-magenta: {self.colors.magenta};
            --color-magenta-dim: {self.colors.magenta_dim};
            --color-magenta-glow: {self.colors.magenta_glow};

            --color-green: {self.colors.green};
            --color-green-dim: {self.colors.green_dim};
            --color-green-glow: {self.colors.green_glow};

            --color-orange: {self.colors.orange};
            --color-orange-dim: {self.colors.orange_dim};
            --color-orange-glow: {self.colors.orange_glow};

            --color-red: {self.colors.red};
            --color-red-dim: {self.colors.red_dim};
            --color-red-glow: {self.colors.red_glow};

            --color-yellow: {self.colors.yellow};
            --color-yellow-dim: {self.colors.yellow_dim};
            --color-yellow-glow: {self.colors.yellow_glow};

            /* Text */
            --text-white: {self.colors.white};
            --text-white-dim: {self.colors.white_dim};
            --text-muted: {self.colors.muted};
            --text-muted-dim: {self.colors.muted_dim};

            /* Typography */
            --font-family-base: {self.typography.font_family_base};
            --font-family-mono: {self.typography.font_family_mono};

            /* Spacing */
            --space-1: {self.spacing.space_1};
            --space-2: {self.spacing.space_2};
            --space-3: {self.spacing.space_3};
            --space-4: {self.spacing.space_4};
            --space-6: {self.spacing.space_6};
            --space-8: {self.spacing.space_8};

            /* Borders */
            --radius-base: {self.borders.radius_base};
            --radius-lg: {self.borders.radius_lg};
            --radius-xl: {self.borders.radius_xl};

            /* Shadows */
            --shadow-md: {self.shadows.shadow_md};
            --shadow-lg: {self.shadows.shadow_lg};
            --glow-cyan: {self.shadows.glow_cyan};
            --glow-purple: {self.shadows.glow_purple};
            --glow-green: {self.shadows.glow_green};
            --glow-red: {self.shadows.glow_red};

            /* Animation */
            --duration-base: {self.animation.duration_base};
            --ease-in-out: {self.animation.ease_in_out};
        }}
        """

    def get_global_css(self) -> str:
        """Generate global CSS for the theme."""
        return f"""
        {self.get_css_variables()}

        /* Base styles */
        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}

        body {{
            font-family: var(--font-family-base);
            background-color: var(--bg-base);
            color: var(--text-white);
            line-height: 1.5;
        }}

        /* Keyframe animations */
        @keyframes fadeIn {{
            from {{
                opacity: 0;
            }}
            to {{
                opacity: 1;
            }}
        }}

        @keyframes fadeInDown {{
            from {{
                opacity: 0;
                transform: translateY(-20px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}

        @keyframes fadeInUp {{
            from {{
                opacity: 0;
                transform: translateY(20px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}

        @keyframes slideIn {{
            from {{
                transform: translateX(-100%);
                opacity: 0;
            }}
            to {{
                transform: translateX(0);
                opacity: 1;
            }}
        }}

        @keyframes pulse {{
            0%, 100% {{
                opacity: 1;
            }}
            50% {{
                opacity: 0.7;
            }}
        }}

        @keyframes glowPulse {{
            0%, 100% {{
                box-shadow: 0 0 20px rgba(0, 245, 255, 0.3);
            }}
            50% {{
                box-shadow: 0 0 30px rgba(0, 245, 255, 0.5);
            }}
        }}

        /* Reduced motion support */
        @media (prefers-reduced-motion: reduce) {{
            *,
            *::before,
            *::after {{
                animation-duration: 0.01ms !important;
                animation-iteration-count: 1 !important;
                transition-duration: 0.01ms !important;
            }}
        }}
        """


# Global theme instance
neon_theme = NeonTheme()
