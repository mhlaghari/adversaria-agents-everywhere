export type TaskCapability = "research" | "write" | "visualize" | "present";

export const CAPABILITY_OPTIONS: ReadonlyArray<{
  value: TaskCapability;
  label: string;
  adapterSlugs: readonly string[];
}> = [
  { value: "research", label: "Research", adapterSlugs: ["deep-research"] },
  {
    value: "write",
    label: "Write",
    adapterSlugs: [
      "meeting-grounded-writing",
      "architecture-doc",
      "marketing-copy",
    ],
  },
  { value: "visualize", label: "Visualize", adapterSlugs: ["drawio-diagram"] },
  { value: "present", label: "Present", adapterSlugs: ["slides-deck"] },
];

/** What the finished artifact is called, for "… ready" copy. */
export const CAPABILITY_ARTIFACT_NOUN: Record<TaskCapability, string> = {
  research: "Research",
  write: "Draft",
  visualize: "Diagram",
  present: "Deck",
};

export function isTaskCapability(value: string): value is TaskCapability {
  return CAPABILITY_OPTIONS.some((option) => option.value === value);
}
