"use client";

const PARTICLE_COUNT = 300;
const COLORS = ["#f59e0b", "#00a6ff", "#ff0056", "#6500ff"];

function Particle({ i }: { i: number }) {
  const size = 4 + (i % 3);
  const left = ((i * 37 + i * i * 7) % 97) + 1;
  const top = ((i * 53 + i * 11) % 97) + 1;
  const color = COLORS[i % COLORS.length];
  const duration = 12 + (i % 15);
  const delay = (i * 0.08) % 4;

  return (
    <div
      className="absolute rounded-full animate-float"
      style={{
        width: size,
        height: size,
        left: `${left}%`,
        top: `${top}%`,
        backgroundColor: color,
        opacity: 0.7,
        animationDuration: `${duration}s`,
        animationDelay: `${delay}s`,
      }}
    />
  );
}

export function CSSParticleField() {
  return (
    <div className="pointer-events-none absolute inset-0 overflow-hidden">
      {Array.from({ length: PARTICLE_COUNT }, (_, i) => (
        <Particle key={i} i={i} />
      ))}
    </div>
  );
}
