import {commonSx} from "../../theme.js";

export const pageSx = commonSx.page;
export const pageInnerSx = commonSx.pageInner;
export const sectionPaperSx = commonSx.panel;
export const sectionTitleSx = commonSx.sectionTitle;
export const subsectionTitleSx = commonSx.subsectionTitle;
export const textFieldSx = commonSx.field;
export const selectFieldSx = commonSx.field;

export const headerStackSx = {
    display: "grid",
    gap: 2,
};

export const headerTripleRowSx = {
    display: "grid",
    gridTemplateColumns: {
        xs: "1fr",
        md: "repeat(3, minmax(0, 1fr))",
    },
    gap: 2,
    alignItems: "stretch",
};

export const headerOwnerRowSx = {
    display: "grid",
    gridTemplateColumns: {
        xs: "1fr",
        md: "repeat(2, minmax(0, 1fr))",
    },
    gap: 2,
    alignItems: "stretch",
};

export const headerOwnerFieldSx = {
    ...commonSx.field,
    height: "100%",
    "& .MuiInputBase-root": {
        height: "100%",
        alignItems: "center",
    },
};
