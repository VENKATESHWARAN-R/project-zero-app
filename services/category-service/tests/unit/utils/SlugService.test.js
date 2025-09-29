const SlugService = require('../../../src/services/SlugService');
const { Category } = require('../../../src/models');

// Mock dependencies
jest.mock('../../../src/models');

describe('SlugService', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('generateSlug', () => {
    it('should generate URL-friendly slug from name', async () => {
      const name = 'Test Category Name';
      Category.findOne.mockResolvedValue(null); // No existing slug

      const slug = await SlugService.generateSlug(name);

      expect(slug).toBe('test-category-name');
    });

    it('should handle special characters and spaces', async () => {
      const name = 'Test & Category - Name!';
      Category.findOne.mockResolvedValue(null);

      const slug = await SlugService.generateSlug(name);

      expect(slug).toMatch(/^[a-z0-9-]+$/); // Only lowercase, numbers, and hyphens
      expect(slug).not.toContain(' ');
      expect(slug).not.toContain('&');
      expect(slug).not.toContain('!');
    });

    it('should handle Unicode characters', async () => {
      const name = 'Café & Résumé';
      Category.findOne.mockResolvedValue(null);

      const slug = await SlugService.generateSlug(name);

      expect(slug).toMatch(/^[a-z0-9-]+$/);
    });

    it('should handle very long names', async () => {
      const name = 'A'.repeat(200);
      Category.findOne.mockResolvedValue(null);

      const slug = await SlugService.generateSlug(name);

      expect(slug.length).toBeLessThanOrEqual(120); // Max slug length
    });

    it('should append number for duplicate slugs', async () => {
      const name = 'Test Category';

      // Mock existing slug
      Category.findOne.mockResolvedValueOnce({ slug: 'test-category' });
      Category.findOne.mockResolvedValueOnce(null); // Second attempt is unique

      const slug = await SlugService.generateSlug(name);

      expect(slug).toBe('test-category-1');
    });

    it('should increment number for multiple duplicates', async () => {
      const name = 'Test Category';

      // Mock multiple existing slugs
      Category.findOne.mockResolvedValueOnce({ slug: 'test-category' });
      Category.findOne.mockResolvedValueOnce({ slug: 'test-category-1' });
      Category.findOne.mockResolvedValueOnce({ slug: 'test-category-2' });
      Category.findOne.mockResolvedValueOnce(null); // Fourth attempt is unique

      const slug = await SlugService.generateSlug(name);

      expect(slug).toBe('test-category-3');
    });

    it('should handle empty or whitespace-only names', async () => {
      const name = '   ';
      Category.findOne.mockResolvedValue(null);

      const slug = await SlugService.generateSlug(name);

      expect(slug).toBeTruthy();
      expect(slug.length).toBeGreaterThan(0);
    });
  });

  describe('validateSlug', () => {
    it('should return true for valid slug', () => {
      const validSlugs = [
        'test-category',
        'category-123',
        'a',
        'test-category-name-with-many-words'
      ];

      validSlugs.forEach(slug => {
        expect(SlugService.validateSlug(slug)).toBe(true);
      });
    });

    it('should return false for invalid slug', () => {
      const invalidSlugs = [
        'Test Category', // Contains spaces
        'test_category', // Contains underscores
        'test@category', // Contains special characters
        'test category!', // Contains spaces and special chars
        '', // Empty string
        'A'.repeat(121), // Too long
        '-test', // Starts with hyphen
        'test-', // Ends with hyphen
        '--test', // Multiple consecutive hyphens
      ];

      invalidSlugs.forEach(slug => {
        expect(SlugService.validateSlug(slug)).toBe(false);
      });
    });
  });

  describe('isSlugUnique', () => {
    it('should return true when slug is unique', async () => {
      Category.findOne.mockResolvedValue(null);

      const result = await SlugService.isSlugUnique('unique-slug');

      expect(result).toBe(true);
      expect(Category.findOne).toHaveBeenCalledWith({
        where: { slug: 'unique-slug' }
      });
    });

    it('should return false when slug exists', async () => {
      Category.findOne.mockResolvedValue({ id: 1, slug: 'existing-slug' });

      const result = await SlugService.isSlugUnique('existing-slug');

      expect(result).toBe(false);
    });

    it('should exclude specific category ID when checking uniqueness', async () => {
      Category.findOne.mockResolvedValue(null);

      const result = await SlugService.isSlugUnique('test-slug', 1);

      expect(Category.findOne).toHaveBeenCalledWith({
        where: {
          slug: 'test-slug',
          id: { [expect.any(Symbol)]: 1 } // Sequelize Op.ne
        }
      });
      expect(result).toBe(true);
    });
  });

  describe('updateSlug', () => {
    it('should update slug for existing category', async () => {
      const categoryId = 1;
      const newName = 'Updated Category Name';

      const mockCategory = {
        id: categoryId,
        name: 'Old Name',
        slug: 'old-name',
        update: jest.fn().mockResolvedValue(true)
      };

      Category.findByPk.mockResolvedValue(mockCategory);
      Category.findOne.mockResolvedValue(null); // New slug is unique

      const result = await SlugService.updateSlug(categoryId, newName);

      expect(mockCategory.update).toHaveBeenCalledWith({
        slug: 'updated-category-name'
      });
      expect(result).toBe('updated-category-name');
    });

    it('should return null when category not found', async () => {
      Category.findByPk.mockResolvedValue(null);

      const result = await SlugService.updateSlug(999, 'Any Name');

      expect(result).toBeNull();
    });
  });

  describe('slugify helper', () => {
    it('should convert text to lowercase', () => {
      const result = SlugService.slugify('TEST CATEGORY');
      expect(result).toBe('test-category');
    });

    it('should replace spaces with hyphens', () => {
      const result = SlugService.slugify('test category name');
      expect(result).toBe('test-category-name');
    });

    it('should remove special characters', () => {
      const result = SlugService.slugify('test@#$%^&*()category');
      expect(result).toBe('testcategory');
    });

    it('should remove multiple consecutive hyphens', () => {
      const result = SlugService.slugify('test---category');
      expect(result).toBe('test-category');
    });

    it('should trim hyphens from start and end', () => {
      const result = SlugService.slugify('-test-category-');
      expect(result).toBe('test-category');
    });
  });
});