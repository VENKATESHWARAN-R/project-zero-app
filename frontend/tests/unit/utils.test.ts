/**
 * Utils function tests
 */

import {
  cn,
  formatPrice,
  formatCurrency,
  formatPriceRange,
  formatDate,
  formatDateTime,
  formatRelativeTime,
  truncate,
  capitalize,
  slugify,
  generateId,
  debounce,
  throttle,
  isEmpty,
  deepClone,
  hasProperty,
  getNestedValue,
  setNestedValue,
  removeUndefined,
  arraysEqual,
  unique,
  groupBy,
  sortBy,
  matchesSearch,
  highlightMatches,
  getPaginationInfo,
  getPaginationRange,
  formatFileSize,
  isValidUrl,
  randomColor,
  formatNumber,
  getInitials,
  sleep,
} from '@/lib/utils';

// Mock Date for consistent testing
const mockDate = new Date('2023-12-01T12:00:00Z');
const originalDate = Date;

beforeAll(() => {
  global.Date = jest.fn(() => mockDate) as any;
  global.Date.now = jest.fn(() => mockDate.getTime());
  Object.setPrototypeOf(global.Date, originalDate);
});

afterAll(() => {
  global.Date = originalDate;
});

describe('Utils Functions', () => {
  describe('cn', () => {
    it('should combine class names', () => {
      expect(cn('class1', 'class2')).toBe('class1 class2');
    });

    it('should handle conditional classes', () => {
      expect(cn('class1', false && 'class2', 'class3')).toBe('class1 class3');
    });

    it('should merge Tailwind classes', () => {
      expect(cn('px-2 py-1', 'px-4')).toBe('py-1 px-4');
    });
  });

  describe('formatPrice', () => {
    it('should format price in cents to currency', () => {
      expect(formatPrice(1250)).toBe('$12.50');
    });

    it('should format price with different currency', () => {
      expect(formatPrice(1250, 'EUR')).toBe('€12.50');
    });

    it('should handle zero price', () => {
      expect(formatPrice(0)).toBe('$0.00');
    });
  });

  describe('formatCurrency', () => {
    it('should be alias for formatPrice', () => {
      expect(formatCurrency(1250)).toBe(formatPrice(1250));
    });
  });

  describe('formatPriceRange', () => {
    it('should format price range', () => {
      expect(formatPriceRange(1000, 2000)).toBe('$10.00 - $20.00');
    });

    it('should format single price when min equals max', () => {
      expect(formatPriceRange(1500, 1500)).toBe('$15.00');
    });
  });

  describe('formatDate', () => {
    it('should format ISO date string', () => {
      const result = formatDate('2023-12-01T12:00:00Z');
      expect(result).toMatch(/December 1, 2023/);
    });
  });

  describe('formatDateTime', () => {
    it('should format ISO date string with time', () => {
      const result = formatDateTime('2023-12-01T12:00:00Z');
      expect(result).toMatch(/Dec 1, 2023/);
      expect(result).toMatch(/12:00/);
    });
  });

  describe('formatRelativeTime', () => {
    it('should return "just now" for recent times', () => {
      const recentTime = new Date(mockDate.getTime() - 30000).toISOString(); // 30 seconds ago
      expect(formatRelativeTime(recentTime)).toBe('just now');
    });

    it('should return minutes ago', () => {
      const pastTime = new Date(mockDate.getTime() - 120000).toISOString(); // 2 minutes ago
      expect(formatRelativeTime(pastTime)).toBe('2 minutes ago');
    });

    it('should return hours ago', () => {
      const pastTime = new Date(mockDate.getTime() - 7200000).toISOString(); // 2 hours ago
      expect(formatRelativeTime(pastTime)).toBe('2 hours ago');
    });

    it('should return days ago', () => {
      const pastTime = new Date(mockDate.getTime() - 172800000).toISOString(); // 2 days ago
      expect(formatRelativeTime(pastTime)).toBe('2 days ago');
    });
  });

  describe('truncate', () => {
    it('should truncate long text', () => {
      const longText = 'This is a very long text that should be truncated';
      expect(truncate(longText, 20)).toBe('This is a very long...');
    });

    it('should not truncate short text', () => {
      const shortText = 'Short text';
      expect(truncate(shortText, 20)).toBe('Short text');
    });
  });

  describe('capitalize', () => {
    it('should capitalize first letter of each word', () => {
      expect(capitalize('hello world')).toBe('Hello World');
    });

    it('should handle single word', () => {
      expect(capitalize('hello')).toBe('Hello');
    });
  });

  describe('slugify', () => {
    it('should convert text to slug format', () => {
      expect(slugify('Hello World Test')).toBe('hello-world-test');
    });

    it('should remove special characters', () => {
      expect(slugify('Hello! @World# $Test%')).toBe('hello-world-test');
    });

    it('should handle multiple spaces and hyphens', () => {
      expect(slugify('Hello   World---Test')).toBe('hello-world-test');
    });
  });

  describe('generateId', () => {
    it('should generate unique ID', () => {
      const id1 = generateId();
      const id2 = generateId();
      expect(id1).not.toBe(id2);
    });

    it('should generate ID with prefix', () => {
      const id = generateId('test');
      expect(id).toMatch(/^test-/);
    });
  });

  describe('debounce', () => {
    it('should debounce function calls', async () => {
      const mockFn = jest.fn();
      const debouncedFn = debounce(mockFn, 100);

      debouncedFn('arg1');
      debouncedFn('arg2');
      debouncedFn('arg3');

      expect(mockFn).not.toHaveBeenCalled();

      await sleep(150);
      expect(mockFn).toHaveBeenCalledTimes(1);
      expect(mockFn).toHaveBeenCalledWith('arg3');
    });
  });

  describe('throttle', () => {
    it('should throttle function calls', async () => {
      const mockFn = jest.fn();
      const throttledFn = throttle(mockFn, 100);

      throttledFn('arg1');
      throttledFn('arg2');
      throttledFn('arg3');

      expect(mockFn).toHaveBeenCalledTimes(1);
      expect(mockFn).toHaveBeenCalledWith('arg1');
    });
  });

  describe('isEmpty', () => {
    it('should detect empty values', () => {
      expect(isEmpty(null)).toBe(true);
      expect(isEmpty(undefined)).toBe(true);
      expect(isEmpty('')).toBe(true);
      expect(isEmpty('   ')).toBe(true);
      expect(isEmpty([])).toBe(true);
      expect(isEmpty({})).toBe(true);
    });

    it('should detect non-empty values', () => {
      expect(isEmpty('hello')).toBe(false);
      expect(isEmpty([1, 2, 3])).toBe(false);
      expect(isEmpty({ key: 'value' })).toBe(false);
      expect(isEmpty(0)).toBe(false);
      expect(isEmpty(false)).toBe(false);
    });
  });

  describe('deepClone', () => {
    it('should deep clone objects', () => {
      const original = { a: 1, b: { c: 2 } };
      const cloned = deepClone(original);

      expect(cloned).toEqual(original);
      expect(cloned).not.toBe(original);
      expect(cloned.b).not.toBe(original.b);
    });

    it('should clone arrays', () => {
      const original = [1, 2, { a: 3 }];
      const cloned = deepClone(original);

      expect(cloned).toEqual(original);
      expect(cloned).not.toBe(original);
      expect(cloned[2]).not.toBe(original[2]);
    });

    it('should clone dates', () => {
      const original = new Date('2023-01-01');
      const cloned = deepClone(original);

      expect(cloned).toEqual(original);
      expect(cloned).not.toBe(original);
    });
  });

  describe('hasProperty', () => {
    it('should check if object has property', () => {
      const obj = { key1: 'value1', key2: 'value2' };
      expect(hasProperty(obj, 'key1')).toBe(true);
      expect(hasProperty(obj, 'key3')).toBe(false);
    });
  });

  describe('getNestedValue', () => {
    it('should get nested object property', () => {
      const obj = { a: { b: { c: 'value' } } };
      expect(getNestedValue(obj, 'a.b.c')).toBe('value');
    });

    it('should return undefined for non-existent path', () => {
      const obj = { a: { b: { c: 'value' } } };
      expect(getNestedValue(obj, 'a.b.d')).toBeUndefined();
    });
  });

  describe('setNestedValue', () => {
    it('should set nested object property', () => {
      const obj = { a: { b: {} } };
      setNestedValue(obj, 'a.b.c', 'value');
      expect(obj.a.b.c).toBe('value');
    });

    it('should create nested structure if not exists', () => {
      const obj = {};
      setNestedValue(obj, 'a.b.c', 'value');
      expect((obj as any).a.b.c).toBe('value');
    });
  });

  describe('removeUndefined', () => {
    it('should remove undefined properties', () => {
      const obj = { a: 1, b: undefined, c: 'test', d: null };
      const result = removeUndefined(obj);
      expect(result).toEqual({ a: 1, c: 'test', d: null });
    });
  });

  describe('arraysEqual', () => {
    it('should compare arrays for equality', () => {
      expect(arraysEqual([1, 2, 3], [1, 2, 3])).toBe(true);
      expect(arraysEqual([1, 2, 3], [1, 2, 4])).toBe(false);
      expect(arraysEqual([1, 2, 3], [1, 2])).toBe(false);
    });
  });

  describe('unique', () => {
    it('should return unique items from array', () => {
      expect(unique([1, 2, 2, 3, 3, 4])).toEqual([1, 2, 3, 4]);
    });

    it('should handle empty array', () => {
      expect(unique([])).toEqual([]);
    });
  });

  describe('groupBy', () => {
    it('should group array items by key', () => {
      const items = [
        { type: 'fruit', name: 'apple' },
        { type: 'fruit', name: 'banana' },
        { type: 'vegetable', name: 'carrot' },
      ];

      const grouped = groupBy(items, 'type');
      expect(grouped).toEqual({
        fruit: [
          { type: 'fruit', name: 'apple' },
          { type: 'fruit', name: 'banana' },
        ],
        vegetable: [{ type: 'vegetable', name: 'carrot' }],
      });
    });
  });

  describe('sortBy', () => {
    it('should sort by single criterion', () => {
      const items = [{ age: 30 }, { age: 20 }, { age: 25 }];
      const sorted = sortBy(items, item => item.age);
      expect(sorted).toEqual([{ age: 20 }, { age: 25 }, { age: 30 }]);
    });

    it('should sort by multiple criteria', () => {
      const items = [
        { name: 'John', age: 30 },
        { name: 'Alice', age: 25 },
        { name: 'Alice', age: 30 },
      ];
      const sorted = sortBy(items, item => item.name, item => item.age);
      expect(sorted).toEqual([
        { name: 'Alice', age: 25 },
        { name: 'Alice', age: 30 },
        { name: 'John', age: 30 },
      ]);
    });
  });

  describe('matchesSearch', () => {
    it('should check if text matches search query', () => {
      expect(matchesSearch('Hello World', 'hello')).toBe(true);
      expect(matchesSearch('Hello World', 'world')).toBe(true);
      expect(matchesSearch('Hello World', 'test')).toBe(false);
    });

    it('should return true for empty query', () => {
      expect(matchesSearch('Hello World', '')).toBe(true);
    });
  });

  describe('highlightMatches', () => {
    it('should highlight search matches', () => {
      expect(highlightMatches('Hello World', 'world')).toBe('Hello <mark>World</mark>');
    });

    it('should return original text for empty query', () => {
      expect(highlightMatches('Hello World', '')).toBe('Hello World');
    });
  });

  describe('getPaginationInfo', () => {
    it('should calculate pagination info', () => {
      const info = getPaginationInfo(2, 100, 10);
      expect(info).toEqual({
        totalPages: 10,
        startItem: 11,
        endItem: 20,
        hasNext: true,
        hasPrev: true,
        isFirstPage: false,
        isLastPage: false,
      });
    });

    it('should handle first page', () => {
      const info = getPaginationInfo(1, 100, 10);
      expect(info.isFirstPage).toBe(true);
      expect(info.hasPrev).toBe(false);
    });

    it('should handle last page', () => {
      const info = getPaginationInfo(10, 100, 10);
      expect(info.isLastPage).toBe(true);
      expect(info.hasNext).toBe(false);
    });
  });

  describe('getPaginationRange', () => {
    it('should generate pagination range', () => {
      expect(getPaginationRange(5, 10, 5)).toEqual([3, 4, 5, 6, 7]);
    });

    it('should handle start boundary', () => {
      expect(getPaginationRange(2, 10, 5)).toEqual([1, 2, 3, 4, 5]);
    });

    it('should handle end boundary', () => {
      expect(getPaginationRange(9, 10, 5)).toEqual([6, 7, 8, 9, 10]);
    });

    it('should return all pages when total is less than max', () => {
      expect(getPaginationRange(3, 4, 5)).toEqual([1, 2, 3, 4]);
    });
  });

  describe('formatFileSize', () => {
    it('should format file sizes', () => {
      expect(formatFileSize(0)).toBe('0 Bytes');
      expect(formatFileSize(1024)).toBe('1 KB');
      expect(formatFileSize(1024 * 1024)).toBe('1 MB');
      expect(formatFileSize(1536)).toBe('1.5 KB');
    });
  });

  describe('isValidUrl', () => {
    it('should validate URLs', () => {
      expect(isValidUrl('https://example.com')).toBe(true);
      expect(isValidUrl('http://localhost:3000')).toBe(true);
      expect(isValidUrl('not-a-url')).toBe(false);
      expect(isValidUrl('')).toBe(false);
    });
  });

  describe('randomColor', () => {
    it('should generate hex color', () => {
      const color = randomColor();
      expect(color).toMatch(/^#[0-9a-f]{6}$/i);
    });
  });

  describe('formatNumber', () => {
    it('should format numbers with commas', () => {
      expect(formatNumber(1234)).toBe('1,234');
      expect(formatNumber(1234567)).toBe('1,234,567');
    });
  });

  describe('getInitials', () => {
    it('should generate initials', () => {
      expect(getInitials('John Doe')).toBe('JD');
      expect(getInitials('Alice Bob Charlie')).toBe('AB');
      expect(getInitials('Test')).toBe('T');
    });
  });

  describe('sleep', () => {
    it('should delay execution', async () => {
      const start = Date.now();
      await sleep(100);
      const end = Date.now();
      expect(end - start).toBeGreaterThanOrEqual(95); // Allow for small timing variations
    });
  });
});