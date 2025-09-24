/**
 * Validation schema tests
 * Tests all Zod validation schemas and helper functions
 */

import {
  loginSchema,
  registerSchema,
  productSearchSchema,
  productFiltersSchema,
  addToCartSchema,
  updateCartItemSchema,
  contactFormSchema,
  newsletterSchema,
  profileUpdateSchema,
  passwordChangeSchema,
  validateEmail,
  validatePassword,
  validateQuantity,
  sanitizeSearchQuery,
  validatePriceRange,
  getValidationRules,
} from '@/lib/validations';

describe('Validation Schemas', () => {
  describe('loginSchema', () => {
    it('should validate correct login data', () => {
      const validData = {
        email: 'test@example.com',
        password: 'password123',
      };

      const result = loginSchema.safeParse(validData);
      expect(result.success).toBe(true);
    });

    it('should reject invalid email', () => {
      const invalidData = {
        email: 'invalid-email',
        password: 'password123',
      };

      const result = loginSchema.safeParse(invalidData);
      expect(result.success).toBe(false);
      if (!result.success) {
        expect(result.error.issues[0].message).toBe('Please enter a valid email address');
      }
    });

    it('should reject short password', () => {
      const invalidData = {
        email: 'test@example.com',
        password: '123',
      };

      const result = loginSchema.safeParse(invalidData);
      expect(result.success).toBe(false);
      if (!result.success) {
        expect(result.error.issues[0].message).toBe('Password must be at least 8 characters long');
      }
    });

    it('should reject empty fields', () => {
      const invalidData = {
        email: '',
        password: '',
      };

      const result = loginSchema.safeParse(invalidData);
      expect(result.success).toBe(false);
      if (!result.success) {
        expect(result.error.issues.length).toBeGreaterThan(0);
        // Should have errors for both email and password fields
        expect(result.error.issues.some(issue => issue.path.includes('email'))).toBe(true);
        expect(result.error.issues.some(issue => issue.path.includes('password'))).toBe(true);
      }
    });
  });

  describe('registerSchema', () => {
    it('should validate correct registration data', () => {
      const validData = {
        email: 'test@example.com',
        password: 'Password123!',
        confirmPassword: 'Password123!',
        firstName: 'John',
        lastName: 'Doe',
      };

      const result = registerSchema.safeParse(validData);
      expect(result.success).toBe(true);
    });

    it('should reject weak password', () => {
      const invalidData = {
        email: 'test@example.com',
        password: 'password', // Missing uppercase, number, special char
        confirmPassword: 'password',
        firstName: 'John',
        lastName: 'Doe',
      };

      const result = registerSchema.safeParse(invalidData);
      expect(result.success).toBe(false);
    });

    it('should reject password mismatch', () => {
      const invalidData = {
        email: 'test@example.com',
        password: 'Password123!',
        confirmPassword: 'Password456!',
        firstName: 'John',
        lastName: 'Doe',
      };

      const result = registerSchema.safeParse(invalidData);
      expect(result.success).toBe(false);
      if (!result.success) {
        expect(result.error.issues[0].message).toBe("Passwords don't match");
      }
    });

    it('should reject invalid names with numbers', () => {
      const invalidData = {
        email: 'test@example.com',
        password: 'Password123!',
        confirmPassword: 'Password123!',
        firstName: 'John123',
        lastName: 'Doe456',
      };

      const result = registerSchema.safeParse(invalidData);
      expect(result.success).toBe(false);
    });

    it('should reject short names', () => {
      const invalidData = {
        email: 'test@example.com',
        password: 'Password123!',
        confirmPassword: 'Password123!',
        firstName: 'J',
        lastName: 'D',
      };

      const result = registerSchema.safeParse(invalidData);
      expect(result.success).toBe(false);
    });
  });

  describe('productSearchSchema', () => {
    it('should validate search query', () => {
      const validData = {
        query: 'laptop computers',
      };

      const result = productSearchSchema.safeParse(validData);
      expect(result.success).toBe(true);
    });

    it('should reject empty query', () => {
      const invalidData = {
        query: '',
      };

      const result = productSearchSchema.safeParse(invalidData);
      expect(result.success).toBe(false);
    });

    it('should reject too long query', () => {
      const invalidData = {
        query: 'a'.repeat(101),
      };

      const result = productSearchSchema.safeParse(invalidData);
      expect(result.success).toBe(false);
    });

    it('should trim whitespace', () => {
      const data = {
        query: '  laptop  ',
      };

      const result = productSearchSchema.safeParse(data);
      expect(result.success).toBe(true);
      if (result.success) {
        expect(result.data.query).toBe('laptop');
      }
    });
  });

  describe('productFiltersSchema', () => {
    it('should validate complete filters', () => {
      const validData = {
        category: 'electronics',
        search: 'laptop',
        min_price: 100,
        max_price: 1000,
        in_stock: true,
        page: 1,
        limit: 20,
        sort: 'price' as const,
        order: 'asc' as const,
      };

      const result = productFiltersSchema.safeParse(validData);
      expect(result.success).toBe(true);
    });

    it('should validate with minimal data', () => {
      const validData = {};

      const result = productFiltersSchema.safeParse(validData);
      expect(result.success).toBe(true);
    });

    it('should reject invalid price range', () => {
      const invalidData = {
        min_price: 1000,
        max_price: 100,
      };

      const result = productFiltersSchema.safeParse(invalidData);
      expect(result.success).toBe(false);
      if (!result.success) {
        expect(result.error.issues[0].message).toBe(
          'Minimum price must be less than or equal to maximum price'
        );
      }
    });

    it('should reject negative prices', () => {
      const invalidData = {
        min_price: -100,
        max_price: -50,
      };

      const result = productFiltersSchema.safeParse(invalidData);
      expect(result.success).toBe(false);
    });

    it('should reject invalid sort option', () => {
      const invalidData = {
        sort: 'invalid_sort',
      };

      const result = productFiltersSchema.safeParse(invalidData);
      expect(result.success).toBe(false);
    });

    it('should reject invalid pagination', () => {
      const invalidData = {
        page: 0,
        limit: 0,
      };

      const result = productFiltersSchema.safeParse(invalidData);
      expect(result.success).toBe(false);
    });
  });

  describe('addToCartSchema', () => {
    it('should validate add to cart data', () => {
      const validData = {
        productId: 'prod_123',
        quantity: 2,
      };

      const result = addToCartSchema.safeParse(validData);
      expect(result.success).toBe(true);
    });

    it('should reject empty product ID', () => {
      const invalidData = {
        productId: '',
        quantity: 1,
      };

      const result = addToCartSchema.safeParse(invalidData);
      expect(result.success).toBe(false);
    });

    it('should reject zero quantity', () => {
      const invalidData = {
        productId: 'prod_123',
        quantity: 0,
      };

      const result = addToCartSchema.safeParse(invalidData);
      expect(result.success).toBe(false);
    });

    it('should reject excessive quantity', () => {
      const invalidData = {
        productId: 'prod_123',
        quantity: 11,
      };

      const result = addToCartSchema.safeParse(invalidData);
      expect(result.success).toBe(false);
    });
  });

  describe('updateCartItemSchema', () => {
    it('should validate cart item update', () => {
      const validData = {
        itemId: 'item_123',
        quantity: 3,
      };

      const result = updateCartItemSchema.safeParse(validData);
      expect(result.success).toBe(true);
    });

    it('should allow zero quantity for removal', () => {
      const validData = {
        itemId: 'item_123',
        quantity: 0,
      };

      const result = updateCartItemSchema.safeParse(validData);
      expect(result.success).toBe(true);
    });

    it('should reject negative quantity', () => {
      const invalidData = {
        itemId: 'item_123',
        quantity: -1,
      };

      const result = updateCartItemSchema.safeParse(invalidData);
      expect(result.success).toBe(false);
    });
  });

  describe('contactFormSchema', () => {
    it('should validate contact form data', () => {
      const validData = {
        name: 'John Doe',
        email: 'john@example.com',
        subject: 'Product inquiry',
        message: 'I would like to know more about your products.',
      };

      const result = contactFormSchema.safeParse(validData);
      expect(result.success).toBe(true);
    });

    it('should reject short subject', () => {
      const invalidData = {
        name: 'John Doe',
        email: 'john@example.com',
        subject: 'Hi',
        message: 'This is a test message.',
      };

      const result = contactFormSchema.safeParse(invalidData);
      expect(result.success).toBe(false);
    });

    it('should reject short message', () => {
      const invalidData = {
        name: 'John Doe',
        email: 'john@example.com',
        subject: 'Product inquiry',
        message: 'Short',
      };

      const result = contactFormSchema.safeParse(invalidData);
      expect(result.success).toBe(false);
    });
  });

  describe('newsletterSchema', () => {
    it('should validate email subscription', () => {
      const validData = {
        email: 'subscribe@example.com',
      };

      const result = newsletterSchema.safeParse(validData);
      expect(result.success).toBe(true);
    });

    it('should reject invalid email', () => {
      const invalidData = {
        email: 'invalid-email',
      };

      const result = newsletterSchema.safeParse(invalidData);
      expect(result.success).toBe(false);
    });
  });

  describe('profileUpdateSchema', () => {
    it('should validate profile update data', () => {
      const validData = {
        firstName: 'John',
        lastName: 'Doe',
        email: 'john.doe@example.com',
      };

      const result = profileUpdateSchema.safeParse(validData);
      expect(result.success).toBe(true);
    });
  });

  describe('passwordChangeSchema', () => {
    it('should validate password change data', () => {
      const validData = {
        currentPassword: 'OldPassword123!',
        newPassword: 'NewPassword123!',
        confirmNewPassword: 'NewPassword123!',
      };

      const result = passwordChangeSchema.safeParse(validData);
      expect(result.success).toBe(true);
    });

    it('should reject password mismatch', () => {
      const invalidData = {
        currentPassword: 'OldPassword123!',
        newPassword: 'NewPassword123!',
        confirmNewPassword: 'DifferentPassword123!',
      };

      const result = passwordChangeSchema.safeParse(invalidData);
      expect(result.success).toBe(false);
      if (!result.success) {
        expect(result.error.issues[0].message).toBe("New passwords don't match");
      }
    });
  });
});

describe('Validation Helper Functions', () => {
  describe('validateEmail', () => {
    it('should validate correct email addresses', () => {
      expect(validateEmail('test@example.com')).toBe(true);
      expect(validateEmail('user.name@domain.co.uk')).toBe(true);
      expect(validateEmail('123@456.org')).toBe(true);
    });

    it('should reject invalid email addresses', () => {
      expect(validateEmail('invalid-email')).toBe(false);
      expect(validateEmail('@example.com')).toBe(false);
      expect(validateEmail('test@')).toBe(false);
      expect(validateEmail('')).toBe(false);
    });
  });

  describe('validatePassword', () => {
    it('should validate strong passwords', () => {
      const result = validatePassword('StrongPassword123!');
      expect(result.isValid).toBe(true);
      expect(result.errors).toHaveLength(0);
    });

    it('should identify weak passwords', () => {
      const result = validatePassword('weak');
      expect(result.isValid).toBe(false);
      expect(result.errors).toContain('Password must be at least 8 characters long');
      expect(result.errors).toContain('Password must contain at least one uppercase letter');
      expect(result.errors).toContain('Password must contain at least one number');
      expect(result.errors).toContain('Password must contain at least one special character');
    });

    it('should identify missing character types', () => {
      const testCases = [
        {
          password: 'nouppercase123!',
          expectedError: 'Password must contain at least one uppercase letter',
        },
        {
          password: 'NOLOWERCASE123!',
          expectedError: 'Password must contain at least one lowercase letter',
        },
        {
          password: 'NoNumbers!',
          expectedError: 'Password must contain at least one number',
        },
        {
          password: 'NoSpecialChars123',
          expectedError: 'Password must contain at least one special character',
        },
      ];

      testCases.forEach(({ password, expectedError }) => {
        const result = validatePassword(password);
        expect(result.isValid).toBe(false);
        expect(result.errors).toContain(expectedError);
      });
    });
  });

  describe('validateQuantity', () => {
    it('should validate correct quantities', () => {
      const result = validateQuantity(3, 10);
      expect(result.isValid).toBe(true);
      expect(result.error).toBeUndefined();
    });

    it('should reject zero or negative quantities', () => {
      const result1 = validateQuantity(0, 10);
      expect(result1.isValid).toBe(false);
      expect(result1.error).toBe('Quantity must be greater than 0');

      const result2 = validateQuantity(-1, 10);
      expect(result2.isValid).toBe(false);
      expect(result2.error).toBe('Quantity must be greater than 0');
    });

    it('should reject excessive quantities', () => {
      const result = validateQuantity(11, 20);
      expect(result.isValid).toBe(false);
      expect(result.error).toBe('Maximum quantity per item is 10');
    });

    it('should reject quantities exceeding stock', () => {
      const result = validateQuantity(5, 3);
      expect(result.isValid).toBe(false);
      expect(result.error).toBe('Only 3 items available');
    });
  });

  describe('sanitizeSearchQuery', () => {
    it('should remove dangerous characters', () => {
      expect(sanitizeSearchQuery('<script>alert("xss")</script>')).toBe('scriptalert(xss)/script');
      expect(sanitizeSearchQuery('search & replace')).toBe('search  replace');
      expect(sanitizeSearchQuery("test's query")).toBe('tests query');
    });

    it('should trim whitespace', () => {
      expect(sanitizeSearchQuery('  search query  ')).toBe('search query');
    });

    it('should keep safe characters', () => {
      expect(sanitizeSearchQuery('laptop computer 2023')).toBe('laptop computer 2023');
    });
  });

  describe('validatePriceRange', () => {
    it('should validate correct price ranges', () => {
      const result = validatePriceRange(100, 500);
      expect(result.isValid).toBe(true);
      expect(result.error).toBeUndefined();
    });

    it('should validate single price values', () => {
      const result1 = validatePriceRange(100);
      expect(result1.isValid).toBe(true);

      const result2 = validatePriceRange(undefined, 500);
      expect(result2.isValid).toBe(true);
    });

    it('should reject negative prices', () => {
      const result1 = validatePriceRange(-100, 500);
      expect(result1.isValid).toBe(false);
      expect(result1.error).toBe('Minimum price must be positive');

      const result2 = validatePriceRange(100, -500);
      expect(result2.isValid).toBe(false);
      expect(result2.error).toBe('Maximum price must be positive');
    });

    it('should reject invalid ranges', () => {
      const result = validatePriceRange(500, 100);
      expect(result.isValid).toBe(false);
      expect(result.error).toBe('Minimum price must be less than maximum price');
    });
  });

  describe('getValidationRules', () => {
    it('should return validation rules object', () => {
      const rules = getValidationRules();

      expect(rules).toHaveProperty('email');
      expect(rules).toHaveProperty('password');
      expect(rules).toHaveProperty('name');
      expect(rules).toHaveProperty('quantity');

      expect(rules.email).toHaveProperty('required');
      expect(rules.email).toHaveProperty('pattern');
      expect(rules.password).toHaveProperty('minLength');
      expect(rules.name).toHaveProperty('maxLength');
      expect(rules.quantity).toHaveProperty('min');
      expect(rules.quantity).toHaveProperty('max');
    });

    it('should have correct validation values', () => {
      const rules = getValidationRules();

      expect(rules.password.minLength.value).toBe(8);
      expect(rules.name.minLength.value).toBe(2);
      expect(rules.name.maxLength.value).toBe(50);
      expect(rules.quantity.min.value).toBe(1);
      expect(rules.quantity.max.value).toBe(10);
    });
  });
});