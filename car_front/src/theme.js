import {createTheme} from "@mui/material/styles";

export const designTokens = {
    colors: {
        black: "#111111",
        white: "#ffffff",
        paper: "#f2f2f2",
        border: "#111111",
        muted: "#666666",
        subtle: "#f5f5f5",
        success: "#d9f2d9",
        danger: "#fff5f5",
        dangerText: "#b3261e",
        warning: "#fff8e1",
    },
    radii: {
        none: 0,
        sm: 4,
        md: 8,
    },
    shadows: {
        none: "none",
        subtle: "4px 4px 0 #111111",
    },
    typography: {
        fontFamily: '"Segoe UI", Arial, sans-serif',
        button: {
            textTransform: "none",
            fontWeight: 700,
        },
    },
};

export const commonSx = {
    page: {
        minHeight: "calc(100vh - 56px)",
        width: "100%",
        bgcolor: designTokens.colors.paper,
        px: 3,
        py: 3,
    },
    pageInner: {
        width: "100%",
        minHeight: "calc(100vh - 112px)",
        border: `2px solid ${designTokens.colors.border}`,
        borderRadius: designTokens.radii.none,
        p: 3,
        bgcolor: designTokens.colors.paper,
        boxShadow: designTokens.shadows.none,
    },
    panel: {
        border: `2px solid ${designTokens.colors.border}`,
        borderRadius: designTokens.radii.none,
        p: 2.5,
        mb: 2.5,
        bgcolor: designTokens.colors.white,
        boxShadow: designTokens.shadows.none,
    },
    card: {
        border: `2px solid ${designTokens.colors.border}`,
        borderRadius: designTokens.radii.none,
        p: 2.5,
        bgcolor: designTokens.colors.white,
        boxShadow: designTokens.shadows.none,
    },
    field: {
        bgcolor: designTokens.colors.white,
        "& .MuiOutlinedInput-root": {
            borderRadius: designTokens.radii.none,
        },
        "& .MuiInputBase-input": {
            fontWeight: 500,
        },
        "& .MuiInputLabel-root": {
            color: designTokens.colors.black,
        },
    },
    primaryButton: {
        bgcolor: designTokens.colors.black,
        color: designTokens.colors.white,
        borderRadius: designTokens.radii.none,
        textTransform: "none",
        fontWeight: 800,
        px: 2.5,
        py: 1,
        boxShadow: designTokens.shadows.none,
        border: `1px solid ${designTokens.colors.black}`,
        "&:hover": {
            bgcolor: "#222222",
            boxShadow: designTokens.shadows.none,
        },
        "&.Mui-disabled": {
            bgcolor: "#cccccc",
            color: designTokens.colors.muted,
            border: "1px solid #999999",
        },
    },
    secondaryButton: {
        borderColor: designTokens.colors.black,
        color: designTokens.colors.black,
        borderRadius: designTokens.radii.none,
        textTransform: "none",
        fontWeight: 800,
        bgcolor: designTokens.colors.white,
        "&:hover": {
            borderColor: designTokens.colors.black,
            bgcolor: "#eeeeee",
        },
    },
    sectionTitle: {
        color: designTokens.colors.black,
        fontWeight: 800,
        mb: 2,
    },
    subsectionTitle: {
        color: designTokens.colors.black,
        fontWeight: 800,
        mt: 2,
        mb: 1.5,
    },
    pill: {
        borderRadius: designTokens.radii.none,
        bgcolor: "#eeeeee",
        color: designTokens.colors.black,
        fontWeight: 500,
    },
    inversePill: {
        borderRadius: designTokens.radii.none,
        bgcolor: designTokens.colors.black,
        color: designTokens.colors.white,
        fontWeight: 700,
    },
    outlinePill: {
        borderRadius: designTokens.radii.none,
        bgcolor: designTokens.colors.white,
        color: designTokens.colors.black,
        border: `1px solid ${designTokens.colors.black}`,
        fontWeight: 700,
    },
};

export const appTheme = createTheme({
    palette: {
        primary: {
            main: designTokens.colors.black,
            contrastText: designTokens.colors.white,
        },
        text: {
            primary: designTokens.colors.black,
            secondary: designTokens.colors.muted,
        },
        background: {
            default: designTokens.colors.paper,
            paper: designTokens.colors.white,
        },
        error: {
            main: designTokens.colors.dangerText,
            contrastText: designTokens.colors.white,
        },
    },
    typography: {
        fontFamily: designTokens.typography.fontFamily,
        h4: {
            fontWeight: 800,
            letterSpacing: 0,
        },
        h5: {
            fontWeight: 800,
            letterSpacing: 0,
        },
        h6: {
            fontWeight: 800,
            letterSpacing: 0,
        },
        button: {
            textTransform: "none",
            fontWeight: 700,
        },
    },
    shape: {
        borderRadius: designTokens.radii.none,
    },
    components: {
        MuiButton: {
            defaultProps: {
                disableElevation: true,
            },
            styleOverrides: {
                root: {
                    borderRadius: designTokens.radii.none,
                    textTransform: "none",
                    fontWeight: 700,
                    boxShadow: "none",
                    minHeight: 40,
                    transition: "all 0.15s ease",
                    "&:hover": {
                        boxShadow: "none",
                    },
                },
                contained: {
                    backgroundColor: designTokens.colors.black,
                    color: designTokens.colors.white,
                    border: `1px solid ${designTokens.colors.black}`,
                    "&:hover": {
                        backgroundColor: "#222222",
                    },
                },
                outlined: {
                    borderColor: designTokens.colors.black,
                    color: designTokens.colors.black,
                    backgroundColor: designTokens.colors.white,
                    "&:hover": {
                        borderColor: designTokens.colors.black,
                        backgroundColor: "#f5f5f5",
                    },
                },
            },
        },
        MuiPaper: {
            styleOverrides: {
                root: {
                    borderRadius: designTokens.radii.none,
                    boxShadow: "none",
                },
            },
        },
        MuiChip: {
            styleOverrides: {
                root: {
                    borderRadius: designTokens.radii.none,
                    fontWeight: 700,
                },
            },
        },
        MuiTextField: {
            defaultProps: {
                variant: "outlined",
            },
            styleOverrides: {
                root: {
                    "& .MuiOutlinedInput-root": {
                        borderRadius: designTokens.radii.none,
                    },
                },
            },
        },
        MuiOutlinedInput: {
            styleOverrides: {
                root: {
                    borderRadius: designTokens.radii.none,
                    backgroundColor: designTokens.colors.white,
                },
            },
        },
        MuiAlert: {
            styleOverrides: {
                root: {
                    borderRadius: designTokens.radii.none,
                },
            },
        },
    },
});

export default appTheme;
