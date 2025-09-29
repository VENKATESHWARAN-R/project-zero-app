const express = require('express');
const CategoryService = require('../services/CategoryService');
const { authenticateToken } = require('../middleware/auth');
const { requireAdmin } = require('../middleware/admin');
const { categoryValidation } = require('../middleware/validation');
const axios = require('axios');

const router = express.Router();

// GET /categories - List categories
router.get(
  '/',
  categoryValidation.list,
  async (req, res, next) => {
    try {
      const options = {
        parent_id: req.query.parent_id === 'null' || req.query.parent_id === undefined
          ? null
          : parseInt(req.query.parent_id) || null,
        include_children: req.query.include_children === 'true',
        include_product_count: req.query.include_product_count === 'true',
        active_only: req.query.active_only !== 'false',
      };

      const result = await CategoryService.getCategories(options);
      res.json(result);
    } catch (error) {
      next(error);
    }
  }
);

// POST /categories - Create category (admin only)
router.post(
  '/',
  authenticateToken,
  requireAdmin,
  categoryValidation.create,
  async (req, res, next) => {
    try {
      const category = await CategoryService.createCategory(req.body);
      res.status(201).json(category);
    } catch (error) {
      next(error);
    }
  }
);

// GET /categories/search - Search categories
router.get(
  '/search',
  categoryValidation.search,
  async (req, res, next) => {
    try {
      const options = {
        active_only: req.query.active_only !== 'false',
      };

      const result = await CategoryService.searchCategories(req.query.q, options);
      res.json(result);
    } catch (error) {
      next(error);
    }
  }
);

// GET /categories/:id - Get category by ID
router.get(
  '/:id',
  categoryValidation.getById,
  async (req, res, next) => {
    try {
      const options = {
        include_children: req.query.include_children === 'true',
        include_ancestors: req.query.include_ancestors === 'true',
        include_product_count: req.query.include_product_count === 'true',
      };

      const category = await CategoryService.getCategoryById(
        parseInt(req.params.id),
        options
      );
      res.json(category);
    } catch (error) {
      next(error);
    }
  }
);

// PUT /categories/:id - Update category (admin only)
router.put(
  '/:id',
  authenticateToken,
  requireAdmin,
  categoryValidation.update,
  async (req, res, next) => {
    try {
      const category = await CategoryService.updateCategory(
        parseInt(req.params.id),
        req.body
      );
      res.json(category);
    } catch (error) {
      next(error);
    }
  }
);

// DELETE /categories/:id - Delete category (admin only)
router.delete(
  '/:id',
  authenticateToken,
  requireAdmin,
  categoryValidation.delete,
  async (req, res, next) => {
    try {
      const force = req.query.force === 'true';
      await CategoryService.deleteCategory(parseInt(req.params.id), force);
      res.status(204).send();
    } catch (error) {
      next(error);
    }
  }
);

// GET /categories/:id/hierarchy - Get category hierarchy
router.get(
  '/:id/hierarchy',
  categoryValidation.getById,
  async (req, res, next) => {
    try {
      const hierarchy = await CategoryService.getCategoryHierarchy(
        parseInt(req.params.id)
      );
      res.json(hierarchy);
    } catch (error) {
      next(error);
    }
  }
);

// GET /categories/:id/products - Get products in category
router.get(
  '/:id/products',
  categoryValidation.products,
  async (req, res, next) => {
    try {
      const categoryId = parseInt(req.params.id);

      // First verify category exists
      const category = await CategoryService.getCategoryById(categoryId);

      // Get pagination parameters
      const page = parseInt(req.query.page) || 1;
      const limit = parseInt(req.query.limit) || 20;
      const includeSubcategories = req.query.include_subcategories === 'true';

      // Call product service to get products
      const productServiceUrl = process.env.PRODUCT_SERVICE_URL || 'http://localhost:8004';

      try {
        const productResponse = await axios.get(
          `${productServiceUrl}/products`,
          {
            params: {
              category_id: categoryId,
              include_subcategories: includeSubcategories,
              page,
              limit,
            },
            timeout: 10000,
          }
        );

        const result = {
          products: productResponse.data.products || [],
          pagination: {
            page,
            limit,
            total: productResponse.data.total || 0,
            pages: Math.ceil((productResponse.data.total || 0) / limit),
            has_next: page * limit < (productResponse.data.total || 0),
            has_prev: page > 1,
          },
          category: {
            id: category.id,
            name: category.name,
            slug: category.slug,
          },
          filters: {
            include_subcategories: includeSubcategories,
          },
        };

        res.json(result);
      } catch (productError) {
        if (productError.code === 'ECONNREFUSED' || productError.code === 'ENOTFOUND') {
          return res.status(503).json({
            error: {
              code: 'SERVICE_UNAVAILABLE',
              message: 'Product catalog service is currently unavailable',
              details: {
                service: 'product-catalog',
                retry_after: '30s',
              },
            },
            timestamp: new Date().toISOString(),
            request_id: req.id,
          });
        }
        throw productError;
      }
    } catch (error) {
      next(error);
    }
  }
);

module.exports = router;