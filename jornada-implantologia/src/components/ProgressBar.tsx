type Props = {
    current: number; // paso actual, empezando en 0
    total: number;
  };
  
  export default function ProgressBar({ current, total }: Props) {
    const progress = (current + 1) / total;
  
    return (
      <div className="mb-8">
        <div className="mb-3 flex items-center justify-between text-xs font-semibold text-[#5b6e80]">
          <span>
            Paso {current + 1} de {total}
          </span>
          <span>{Math.round(progress * 100)}%</span>
        </div>
        <div className="progress-track" role="progressbar" aria-valuemin={0} aria-valuemax={100} aria-valuenow={Math.round(progress * 100)}>
          <div
            className="progress-fill"
            style={{ ["--progress" as string]: progress } as React.CSSProperties}
          />
        </div>
      </div>
    );
  }