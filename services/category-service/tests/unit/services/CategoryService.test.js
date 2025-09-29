const CategoryService = require('../../../src/services/CategoryService');
const { Category } = require('../../../src/models');
const SlugService = require('../../../src/services/SlugService');

// Mock dependencies
jest.mock('../../../src/models');
jest.mock('../../../src/services/SlugService');

describe('CategoryService', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('createCategory', () => {
    it('should create a category with auto-generated slug', async () => {
      const categoryData = {
        name: 'Test Category',
        description: 'Test description',
        parent_id: null
      };

      const expectedSlug = 'test-category';
      SlugService.generateSlug.mockResolvedValue(expectedSlug);

      const mockCategory = {
        id: 1,
        ...categoryData,
        slug: expectedSlug,
        created_at: new Date(),
        updated_at: new Date()
      };

      Category.create.mockResolvedValue(mockCategory);

      const result = await CategoryService.createCategory(categoryData);

      expect(SlugService.generateSlug).toHaveBeenCalledWith(categoryData.name);
      expect(Category.create).toHaveBeenCalledWith({
        ...categoryData,
        slug: expectedSlug
      });
      expect(result).toEqual(mockCategory);
    });

    it('should handle parent_id assignment', async () => {
      const categoryData = {
        name: 'Child Category',
        parent_id: 1
      };

      SlugService.generateSlug.mockResolvedValue('child-category');
      Category.create.mockResolvedValue({ id: 2, ...categoryData });

      await CategoryService.createCategory(categoryData);

      expect(Category.create).toHaveBeenCalledWith({
        ...categoryData,
        slug: 'child-category'
      });
    });
  });

  describe('getCategoryById', () => {
    it('should return category with associations when options provided', async () => {
      const categoryId = 1;
      const options = {
        include_children: true,
        include_ancestors: true
      };

      const mockCategory = {
        id: categoryId,
        name: 'Test Category',
        children: [],
        parent: null
      };

      Category.findByPk.mockResolvedValue(mockCategory);

      const result = await CategoryService.getCategoryById(categoryId, options);

      expect(Category.findByPk).toHaveBeenCalledWith(categoryId, {
        include: expect.arrayContaining([
          expect.objectContaining({ as: 'children' }),
          expect.objectContaining({ as: 'parent' })
        ])
      });
      expect(result).toEqual(mockCategory);
    });

    it('should return null when category not found', async () => {
      Category.findByPk.mockResolvedValue(null);

      const result = await CategoryService.getCategoryById(999);

      expect(result).toBeNull();
    });
  });

  describe('updateCategory', () => {
    it('should update category and regenerate slug if name changed', async () => {
      const categoryId = 1;
      const updateData = {
        name: 'Updated Category Name',
        description: 'Updated description'
      };

      const existingCategory = {
        id: categoryId,
        name: 'Old Name',
        slug: 'old-name',
        description: 'Old description',
        update: jest.fn().mockResolvedValue(true),
        reload: jest.fn()
      };

      Category.findByPk.mockResolvedValue(existingCategory);
      SlugService.generateSlug.mockResolvedValue('updated-category-name');

      const result = await CategoryService.updateCategory(categoryId, updateData);

      expect(SlugService.generateSlug).toHaveBeenCalledWith(updateData.name);
      expect(existingCategory.update).toHaveBeenCalledWith({
        ...updateData,
        slug: 'updated-category-name'
      });
      expect(result).toEqual(existingCategory);
    });

    it('should not regenerate slug if name unchanged', async () => {
      const categoryId = 1;
      const updateData = {
        description: 'Updated description'
      };

      const existingCategory = {
        id: categoryId,
        name: 'Same Name',
        slug: 'same-name',
        update: jest.fn().mockResolvedValue(true),
        reload: jest.fn()
      };

      Category.findByPk.mockResolvedValue(existingCategory);

      await CategoryService.updateCategory(categoryId, updateData);

      expect(SlugService.generateSlug).not.toHaveBeenCalled();
      expect(existingCategory.update).toHaveBeenCalledWith(updateData);
    });
  });

  describe('deleteCategory', () => {
    it('should soft delete category by setting is_active to false', async () => {
      const categoryId = 1;
      const mockCategory = {
        id: categoryId,
        is_active: true,
        update: jest.fn().mockResolvedValue(true)
      };

      Category.findByPk.mockResolvedValue(mockCategory);

      const result = await CategoryService.deleteCategory(categoryId);

      expect(mockCategory.update).toHaveBeenCalledWith({ is_active: false });
      expect(result).toBe(true);
    });

    it('should return false when category not found', async () => {
      Category.findByPk.mockResolvedValue(null);

      const result = await CategoryService.deleteCategory(999);

      expect(result).toBe(false);
    });
  });

  describe('searchCategories', () => {
    it('should search categories by name and description', async () => {
      const query = 'test';
      const options = { active_only: true };

      const mockCategories = [
        { id: 1, name: 'Test Category 1' },
        { id: 2, name: 'Another Test' }
      ];

      Category.findAll.mockResolvedValue(mockCategories);

      const result = await CategoryService.searchCategories(query, options);

      expect(Category.findAll).toHaveBeenCalledWith({
        where: expect.objectContaining({
          is_active: true
        })
      });
      expect(result).toEqual(mockCategories);
    });
  });
});