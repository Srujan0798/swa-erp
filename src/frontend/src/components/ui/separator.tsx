"use client";

import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";

const separatorVariants = cva("shrink-0 bg-border", {
  defaultVariants: {
    orientation: "horizontal",
    decorative: true,
  },
  variants: {
    orientation: {
      horizontal: "h-[1px] w-full",
      vertical: "h-full w-[1px]",
    },
    decorative: {
      true: "aria-hidden",
      false: "",
    },
  },
});

type SeparatorProps = React.HTMLAttributes<HTMLDivElement> &
  VariantProps<typeof separatorVariants>;

function Root({ decorative, orientation, className, ...props }: SeparatorProps) {
  return (
    <div
      role={decorative ? "none" : "separator"}
      aria-orientation={decorative ? undefined : (orientation ?? undefined)}
      aria-hidden={decorative || undefined}
      className={cn(separatorVariants({ orientation, decorative }), className)}
      {...props}
    />
  );
}

export const Separator = Object.assign(Root, {
  displayName: "Separator",
});
