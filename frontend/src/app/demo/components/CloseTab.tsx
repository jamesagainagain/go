"use client";

export function CloseTab() {
  return (
    <div
      className="relative flex flex-1 flex-col items-center justify-center px-6"
      role="tabpanel"
      id="tabpanel-4"
      aria-labelledby="tab-4"
    >
      <p className="relative z-[1] text-center text-3xl font-medium text-stone-600 md:text-4xl">
        We&apos;re not competing with loneliness.
      </p>
      <p className="relative z-[1] mt-4 text-center text-3xl font-semibold text-stone-800 md:text-4xl">
        We&apos;re competing with the sofa.
      </p>
      <p className="relative z-[1] mt-8 text-lg text-stone-600">
        go! makes leaving it effortless.
      </p>
    </div>
  );
}
