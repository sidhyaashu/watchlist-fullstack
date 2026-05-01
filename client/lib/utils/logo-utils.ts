/**
 * Generates a deterministic gradient background based on a ticker symbol.
 */
export const getLogoGradient = (symbol: string) => {
  const colors = [
    ["#2B6BFF", "#5C8DFF"], // Accent Blue
    ["#10A37F", "#36C39B"], // Good Green
    ["#E2557A", "#F0759E"], // Danger Pink
    ["#E29A2B", "#F0B65A"], // Warn Orange
    ["#7A3EB5", "#A668D4"], // Purple
    ["#0B2545", "#2B4570"], // Deep Ink
    ["#5B72A0", "#8FA4CF"], // Steel
    ["#C0365B", "#E2557A"], // Crimson
  ];

  let hash = 0;
  for (let i = 0; i < symbol.length; i++) {
    hash = symbol.charCodeAt(i) + ((hash << 5) - hash);
  }
  
  const index = Math.abs(hash) % colors.length;
  const [start, end] = colors[index];
  
  return `linear-gradient(135deg, ${start} 0%, ${end} 100%)`;
};
