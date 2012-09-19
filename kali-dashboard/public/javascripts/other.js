function next() {
  return {
    value: v = ~~Math.max(10, Math.min(90, v + 10 * (Math.random() - .5)))
  };
};