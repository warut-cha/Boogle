import '@testing-library/jest-dom'

// reactflow requires ResizeObserver which jsdom doesn't provide
;(globalThis as any).ResizeObserver = class ResizeObserver {
  observe() {}
  unobserve() {}
  disconnect() {}
}
