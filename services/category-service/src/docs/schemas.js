/**
 * @swagger
 * components:
 *   schemas:
 *     Category:
 *       type: object
 *       properties:
 *         id:
 *           type: integer
 *           example: 1
 *         name:
 *           type: string
 *           example: "Electronics"
 *         slug:
 *           type: string
 *           example: "electronics"
 *         description:
 *           type: string
 *           nullable: true
 *           example: "Electronic devices and accessories"
 *         image_url:
 *           type: string
 *           nullable: true
 *           format: uri
 *           example: "https://example.com/images/electronics.jpg"
 *         parent_id:
 *           type: integer
 *           nullable: true
 *           example: null
 *         sort_order:
 *           type: integer
 *           example: 0
 *         is_active:
 *           type: boolean
 *           example: true
 *         metadata:
 *           type: object
 *           nullable: true
 *           additionalProperties: true
 *           example:
 *             seo_title: "Electronics - Best Deals"
 *             display_color: "#007bff"
 *         created_at:
 *           type: string
 *           format: date-time
 *           example: "2025-09-29T10:00:00Z"
 *         updated_at:
 *           type: string
 *           format: date-time
 *           example: "2025-09-29T10:00:00Z"
 *         children:
 *           type: array
 *           items:
 *             $ref: '#/components/schemas/Category'
 *           description: "Included when include_children=true"
 *         product_count:
 *           type: integer
 *           description: "Included when include_product_count=true"
 *           example: 42
 *
 *     CategoryCreateRequest:
 *       type: object
 *       required:
 *         - name
 *       properties:
 *         name:
 *           type: string
 *           minLength: 1
 *           maxLength: 100
 *           example: "Gaming Laptops"
 *         description:
 *           type: string
 *           nullable: true
 *           example: "High-performance laptops for gaming"
 *         image_url:
 *           type: string
 *           nullable: true
 *           format: uri
 *           example: "https://example.com/images/gaming-laptops.jpg"
 *         parent_id:
 *           type: integer
 *           nullable: true
 *           example: 5
 *         sort_order:
 *           type: integer
 *           minimum: 0
 *           example: 10
 *         metadata:
 *           type: object
 *           nullable: true
 *           additionalProperties: true
 *
 *     ErrorResponse:
 *       type: object
 *       properties:
 *         error:
 *           type: object
 *           properties:
 *             code:
 *               type: string
 *               example: "VALIDATION_ERROR"
 *             message:
 *               type: string
 *               example: "Invalid category name"
 *             details:
 *               type: object
 *               additionalProperties: true
 *               example:
 *                 field: "name"
 *                 reason: "Name must be between 1 and 100 characters"
 *         timestamp:
 *           type: string
 *           format: date-time
 *           example: "2025-09-29T10:00:00Z"
 *         request_id:
 *           type: string
 *           example: "req_12345"
 */