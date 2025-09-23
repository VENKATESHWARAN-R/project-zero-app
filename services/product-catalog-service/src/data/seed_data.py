"""Sample data seeding logic for the product catalog."""

import logging
from decimal import Decimal

from sqlalchemy.orm import Session

from src.models import CategoryEnum, Product

logger = logging.getLogger(__name__)


def seed_sample_products(db: Session):
    """Seed the database with sample products."""
    sample_products = [
        # Electronics (6 products)
        {
            "name": "Smartphone Pro Max",
            "description": "Latest flagship smartphone with advanced camera system, 5G connectivity, and all-day battery life. Features a stunning 6.7-inch display and premium build quality.",
            "price": Decimal("999.99"),
            "category": CategoryEnum.ELECTRONICS,
            "image_url": "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=400",
            "stock_quantity": 50,
        },
        {
            "name": "Gaming Laptop Ultra",
            "description": "High-performance gaming laptop with RTX graphics, 16GB RAM, and 1TB SSD. Perfect for gaming, content creation, and professional work.",
            "price": Decimal("1299.99"),
            "category": CategoryEnum.ELECTRONICS,
            "image_url": "https://images.unsplash.com/photo-1525547719571-a2d4ac8945e2?w=400",
            "stock_quantity": 25,
        },
        {
            "name": "Wireless Bluetooth Headphones",
            "description": "Premium noise-cancelling wireless headphones with 30-hour battery life. Crystal clear audio quality and comfortable over-ear design.",
            "price": Decimal("199.99"),
            "category": CategoryEnum.ELECTRONICS,
            "image_url": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400",
            "stock_quantity": 100,
        },
        {
            "name": "Tablet Pro 12.9",
            "description": "Professional-grade tablet with Apple M2 chip, 12.9-inch Liquid Retina display, and support for Apple Pencil. Ideal for creativity and productivity.",
            "price": Decimal("599.99"),
            "category": CategoryEnum.ELECTRONICS,
            "image_url": "https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0?w=400",
            "stock_quantity": 35,
        },
        {
            "name": "Smartwatch Series 9",
            "description": "Advanced smartwatch with health monitoring, GPS, and cellular connectivity. Track your fitness goals and stay connected on the go.",
            "price": Decimal("299.99"),
            "category": CategoryEnum.ELECTRONICS,
            "image_url": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=400",
            "stock_quantity": 75,
        },
        {
            "name": "Digital Camera DSLR",
            "description": "Professional DSLR camera with 24MP sensor, 4K video recording, and interchangeable lens system. Perfect for photography enthusiasts.",
            "price": Decimal("799.99"),
            "category": CategoryEnum.ELECTRONICS,
            "image_url": "https://images.unsplash.com/photo-1502920917128-1aa500764cbd?w=400",
            "stock_quantity": 20,
        },
        # Clothing (6 products)
        {
            "name": "Premium Cotton T-Shirt",
            "description": "Soft, breathable 100% organic cotton t-shirt. Available in multiple colors with a comfortable, relaxed fit. Perfect for everyday wear.",
            "price": Decimal("29.99"),
            "category": CategoryEnum.CLOTHING,
            "image_url": "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=400",
            "stock_quantity": 150,
        },
        {
            "name": "Designer Denim Jeans",
            "description": "Classic straight-leg jeans made from premium denim with a modern fit. Durable construction with timeless style that works for any occasion.",
            "price": Decimal("89.99"),
            "category": CategoryEnum.CLOTHING,
            "image_url": "https://images.unsplash.com/photo-1542272604-787c3835535d?w=400",
            "stock_quantity": 80,
        },
        {
            "name": "Running Sneakers Pro",
            "description": "High-performance running shoes with advanced cushioning and breathable mesh upper. Designed for comfort and durability during intense workouts.",
            "price": Decimal("149.99"),
            "category": CategoryEnum.CLOTHING,
            "image_url": "https://images.unsplash.com/photo-1549298916-b41d501d3772?w=400",
            "stock_quantity": 60,
        },
        {
            "name": "Winter Jacket Insulated",
            "description": "Warm, waterproof winter jacket with synthetic insulation. Features multiple pockets and adjustable hood for maximum comfort in cold weather.",
            "price": Decimal("199.99"),
            "category": CategoryEnum.CLOTHING,
            "image_url": "https://images.unsplash.com/photo-1551028719-00167b16eac5?w=400",
            "stock_quantity": 40,
        },
        {
            "name": "Summer Dress Floral",
            "description": "Light and airy summer dress with beautiful floral print. Made from breathable fabric with a flattering A-line silhouette.",
            "price": Decimal("79.99"),
            "category": CategoryEnum.CLOTHING,
            "image_url": "https://images.unsplash.com/photo-1496747611176-843222e1e57c?w=400",
            "stock_quantity": 50,
        },
        {
            "name": "Casual Hoodie",
            "description": "Comfortable pullover hoodie made from soft cotton blend. Features a spacious kangaroo pocket and adjustable drawstring hood.",
            "price": Decimal("59.99"),
            "category": CategoryEnum.CLOTHING,
            "image_url": "https://images.unsplash.com/photo-1556821840-3a63f95609a7?w=400",
            "stock_quantity": 90,
        },
        # Books (4 products)
        {
            "name": "Python Programming Mastery",
            "description": "Comprehensive guide to Python programming covering basics to advanced topics. Includes practical examples and real-world projects for hands-on learning.",
            "price": Decimal("49.99"),
            "category": CategoryEnum.BOOKS,
            "image_url": "https://images.unsplash.com/photo-1516979187457-637abb4f9353?w=400",
            "stock_quantity": 100,
        },
        {
            "name": "The Science Fiction Chronicles",
            "description": "Epic science fiction novel exploring themes of technology, humanity, and the future. A thrilling adventure across galaxies with unforgettable characters.",
            "price": Decimal("14.99"),
            "category": CategoryEnum.BOOKS,
            "image_url": "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=400",
            "stock_quantity": 200,
        },
        {
            "name": "Advanced Physics Textbook",
            "description": "University-level physics textbook covering quantum mechanics, thermodynamics, and electromagnetism. Includes problem sets and detailed explanations.",
            "price": Decimal("129.99"),
            "category": CategoryEnum.BOOKS,
            "image_url": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400",
            "stock_quantity": 30,
        },
        {
            "name": "Culinary Arts Masterclass",
            "description": "Professional cookbook with over 200 recipes from world-renowned chefs. Includes techniques, tips, and beautiful photography of finished dishes.",
            "price": Decimal("34.99"),
            "category": CategoryEnum.BOOKS,
            "image_url": "https://images.unsplash.com/photo-1481627834876-b7833e8f5570?w=400",
            "stock_quantity": 75,
        },
        # Home Goods (4 products)
        {
            "name": "Modern Coffee Table",
            "description": "Sleek glass-top coffee table with sturdy metal legs. Minimalist design that complements any living room decor. Easy to clean and maintain.",
            "price": Decimal("299.99"),
            "category": CategoryEnum.HOME_GOODS,
            "image_url": "https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=400",
            "stock_quantity": 15,
        },
        {
            "name": "LED Desk Lamp Adjustable",
            "description": "Energy-efficient LED desk lamp with adjustable brightness and color temperature. Features USB charging port and flexible positioning arm.",
            "price": Decimal("79.99"),
            "category": CategoryEnum.HOME_GOODS,
            "image_url": "https://images.unsplash.com/photo-1507473885765-e6ed057f782c?w=400",
            "stock_quantity": 45,
        },
        {
            "name": "Kitchen Utensil Set Premium",
            "description": "Complete 15-piece kitchen utensil set made from high-quality stainless steel. Includes all essential tools for cooking and food preparation.",
            "price": Decimal("149.99"),
            "category": CategoryEnum.HOME_GOODS,
            "image_url": "https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=400",
            "stock_quantity": 30,
        },
        {
            "name": "Luxury Bedding Set",
            "description": "Premium 1000-thread-count cotton bedding set including sheets, pillowcases, and duvet cover. Ultra-soft and hypoallergenic materials.",
            "price": Decimal("199.99"),
            "category": CategoryEnum.HOME_GOODS,
            "image_url": "https://images.unsplash.com/photo-1522771739844-6a9f6d5f14af?w=400",
            "stock_quantity": 25,
        },
    ]

    # Add products to database
    created_count = 0
    for product_data in sample_products:
        try:
            # Check if product already exists
            existing = (
                db.query(Product).filter(Product.name == product_data["name"]).first()
            )
            if existing:
                logger.info(
                    f"Product '{product_data['name']}' already exists, skipping"
                )
                continue

            product = Product(**product_data)
            db.add(product)
            created_count += 1

        except Exception as e:
            logger.error(f"Error creating product '{product_data['name']}': {e}")
            continue

    try:
        db.commit()
        logger.info(f"Successfully seeded {created_count} sample products")
    except Exception as e:
        db.rollback()
        logger.error(f"Error committing sample products: {e}")
        raise


def create_test_products(db: Session, count: int = 5):
    """Create test products for development/testing purposes."""
    test_products = []
    for i in range(count):
        product = Product(
            name=f"Test Product {i + 1}",
            description=f"This is test product number {i + 1} for development purposes.",
            price=Decimal("19.99"),
            category=CategoryEnum.ELECTRONICS,
            image_url="https://via.placeholder.com/400",
            stock_quantity=10,
            is_active=True,
        )
        test_products.append(product)

    try:
        db.add_all(test_products)
        db.commit()
        logger.info(f"Created {count} test products")
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating test products: {e}")
        raise
