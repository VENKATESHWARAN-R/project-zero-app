const HierarchyService = require('../../../src/services/HierarchyService');
const { Category } = require('../../../src/models');

// Mock dependencies
jest.mock('../../../src/models');

describe('HierarchyService', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('validateHierarchy', () => {
    it('should return true for valid parent assignment', async () => {
      const categoryId = 2;
      const parentId = 1;

      // Mock category exists
      Category.findByPk.mockResolvedValueOnce({ id: categoryId });
      Category.findByPk.mockResolvedValueOnce({ id: parentId });

      // Mock no circular reference
      HierarchyService.hasCircularReference = jest.fn().mockResolvedValue(false);
      HierarchyService.getDepth = jest.fn().mockResolvedValue(3);

      const result = await HierarchyService.validateHierarchy(categoryId, parentId);

      expect(result.valid).toBe(true);
    });

    it('should return false for circular reference', async () => {
      const categoryId = 1;
      const parentId = 2;

      Category.findByPk.mockResolvedValue({ id: categoryId });
      HierarchyService.hasCircularReference = jest.fn().mockResolvedValue(true);

      const result = await HierarchyService.validateHierarchy(categoryId, parentId);

      expect(result.valid).toBe(false);
      expect(result.error).toContain('circular');
    });

    it('should return false for exceeding max depth', async () => {
      const categoryId = 2;
      const parentId = 1;

      Category.findByPk.mockResolvedValue({ id: categoryId });
      HierarchyService.hasCircularReference = jest.fn().mockResolvedValue(false);
      HierarchyService.getDepth = jest.fn().mockResolvedValue(6); // Exceeds max depth of 5

      const result = await HierarchyService.validateHierarchy(categoryId, parentId);

      expect(result.valid).toBe(false);
      expect(result.error).toContain('depth');
    });

    it('should return false when parent category does not exist', async () => {
      const categoryId = 2;
      const parentId = 999;

      Category.findByPk.mockResolvedValueOnce({ id: categoryId });
      Category.findByPk.mockResolvedValueOnce(null); // Parent not found

      const result = await HierarchyService.validateHierarchy(categoryId, parentId);

      expect(result.valid).toBe(false);
      expect(result.error).toContain('not found');
    });
  });

  describe('hasCircularReference', () => {
    it('should detect direct circular reference', async () => {
      const categoryId = 1;
      const parentId = 1; // Self-reference

      const result = await HierarchyService.hasCircularReference(categoryId, parentId);

      expect(result).toBe(true);
    });

    it('should detect indirect circular reference', async () => {
      const categoryId = 1;
      const parentId = 3;

      // Mock hierarchy: 1 -> 2 -> 3 -> 1 (circular)
      const mockCategories = {
        1: { id: 1, parent_id: 2 },
        2: { id: 2, parent_id: 3 },
        3: { id: 3, parent_id: null }
      };

      Category.findByPk.mockImplementation(id => Promise.resolve(mockCategories[id]));

      const result = await HierarchyService.hasCircularReference(categoryId, parentId);

      expect(result).toBe(true);
    });

    it('should return false for valid hierarchy', async () => {
      const categoryId = 3;
      const parentId = 1;

      // Mock valid hierarchy: 1 -> 2, 3 will become child of 1
      const mockCategories = {
        1: { id: 1, parent_id: null },
        2: { id: 2, parent_id: 1 },
        3: { id: 3, parent_id: null }
      };

      Category.findByPk.mockImplementation(id => Promise.resolve(mockCategories[id]));

      const result = await HierarchyService.hasCircularReference(categoryId, parentId);

      expect(result).toBe(false);
    });
  });

  describe('getDepth', () => {
    it('should calculate depth correctly', async () => {
      const categoryId = 3;

      // Mock hierarchy: 1 -> 2 -> 3 (depth 2)
      const mockCategories = {
        1: { id: 1, parent_id: null },
        2: { id: 2, parent_id: 1 },
        3: { id: 3, parent_id: 2 }
      };

      Category.findByPk.mockImplementation(id => Promise.resolve(mockCategories[id]));

      const depth = await HierarchyService.getDepth(categoryId);

      expect(depth).toBe(2);
    });

    it('should return 0 for root category', async () => {
      const categoryId = 1;

      Category.findByPk.mockResolvedValue({ id: 1, parent_id: null });

      const depth = await HierarchyService.getDepth(categoryId);

      expect(depth).toBe(0);
    });
  });

  describe('getAncestors', () => {
    it('should return ancestors in correct order', async () => {
      const categoryId = 3;

      // Mock hierarchy: 1 -> 2 -> 3
      const mockCategories = {
        1: { id: 1, name: 'Root', parent_id: null },
        2: { id: 2, name: 'Level 1', parent_id: 1 },
        3: { id: 3, name: 'Level 2', parent_id: 2 }
      };

      Category.findByPk.mockImplementation(id => Promise.resolve(mockCategories[id]));

      const ancestors = await HierarchyService.getAncestors(categoryId);

      expect(ancestors).toHaveLength(2);
      expect(ancestors[0].name).toBe('Root');
      expect(ancestors[1].name).toBe('Level 1');
    });

    it('should return empty array for root category', async () => {
      const categoryId = 1;

      Category.findByPk.mockResolvedValue({ id: 1, parent_id: null });

      const ancestors = await HierarchyService.getAncestors(categoryId);

      expect(ancestors).toHaveLength(0);
    });
  });

  describe('getDescendants', () => {
    it('should return all descendants', async () => {
      const categoryId = 1;

      const mockDescendants = [
        { id: 2, name: 'Child 1', parent_id: 1 },
        { id: 3, name: 'Child 2', parent_id: 1 },
        { id: 4, name: 'Grandchild', parent_id: 2 }
      ];

      Category.findAll.mockResolvedValue(mockDescendants);

      const descendants = await HierarchyService.getDescendants(categoryId);

      expect(Category.findAll).toHaveBeenCalledWith({
        where: { parent_id: categoryId },
        include: expect.any(Array)
      });
      expect(descendants).toEqual(mockDescendants);
    });
  });

  describe('buildCategoryPath', () => {
    it('should build correct path string', async () => {
      const categoryId = 3;

      // Mock hierarchy
      HierarchyService.getAncestors = jest.fn().mockResolvedValue([
        { name: 'Electronics' },
        { name: 'Computers' }
      ]);

      Category.findByPk.mockResolvedValue({ name: 'Laptops' });

      const path = await HierarchyService.buildCategoryPath(categoryId);

      expect(path).toBe('Electronics > Computers > Laptops');
    });

    it('should return just category name for root', async () => {
      const categoryId = 1;

      HierarchyService.getAncestors = jest.fn().mockResolvedValue([]);
      Category.findByPk.mockResolvedValue({ name: 'Electronics' });

      const path = await HierarchyService.buildCategoryPath(categoryId);

      expect(path).toBe('Electronics');
    });
  });
});