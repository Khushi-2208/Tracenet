export default function ProcessingStatus({ currentStep, steps }) {
  return (
    <div className="glass-card fade-in">
      <h3 className="text-lg font-bold text-gray-200 mb-4">Processing Investigation Dataset</h3>
      <div className="space-y-1">
        {steps.map((step, i) => {
          let status = 'pending';
          if (i < currentStep) status = 'done';
          else if (i === currentStep) status = 'active';

          return (
            <div key={i} className="step-item">
              <div className={`step-icon ${status === 'done' ? 'step-done' : status === 'active' ? 'step-active' : 'step-pending'}`}>
                {status === 'done' ? '✓' : status === 'active' ? '⟳' : '○'}
              </div>
              <span className={status === 'pending' ? 'text-gray-600' : status === 'active' ? 'text-cyber-blue' : 'text-gray-300'}>
                {step}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
