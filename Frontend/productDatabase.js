// Product categories and their base characteristics
const productCategories = {
    electronics: {
        packagingPriorities: ['protection', 'moisture_resistance', 'anti_static'],
        baseEcoScore: [75, 95],
    },
    food: {
        packagingPriorities: ['freshness', 'shelf_life', 'food_safety'],
        baseEcoScore: [70, 90],
    },
    cosmetics: {
        packagingPriorities: ['presentation', 'contamination_prevention', 'durability'],
        baseEcoScore: [65, 88],
    },
    clothing: {
        packagingPriorities: ['moisture_resistance', 'compressibility', 'presentation'],
        baseEcoScore: [80, 95],
    },
    toys: {
        packagingPriorities: ['safety', 'presentation', 'durability'],
        baseEcoScore: [70, 92],
    }
};

const packagingMaterials = {
    'Recycled PET': {
        baseCost: 75,
        sustainability: 92,
        waterResistance: 9,
        durability: 8,
        recyclability: 9
    },
    'Biodegradable Plastic': {
        baseCost: 82,
        sustainability: 88,
        waterResistance: 7,
        durability: 7,
        recyclability: 10
    },
    'Cardboard': {
        baseCost: 60,
        sustainability: 95,
        waterResistance: 4,
        durability: 6,
        recyclability: 10
    },
    'Glass': {
        baseCost: 90,
        sustainability: 85,
        waterResistance: 10,
        durability: 9,
        recyclability: 8
    },
    'Aluminum': {
        baseCost: 85,
        sustainability: 82,
        waterResistance: 10,
        durability: 9,
        recyclability: 9
    },
    'Hemp-based': {
        baseCost: 88,
        sustainability: 96,
        waterResistance: 6,
        durability: 7,
        recyclability: 10
    },
    'Mushroom Packaging': {
        baseCost: 92,
        sustainability: 98,
        waterResistance: 5,
        durability: 6,
        recyclability: 10
    }
};

// Generate 100 products with unique characteristics
const generateProductDatabase = () => {
    const products = {};
    const productList = [
        // Electronics
        'Smartphone', 'Laptop', 'Tablet', 'Smartwatch', 'Headphones', 'Speaker', 'Camera', 'Gaming Console', 
        'Power Bank', 'Router', 'Keyboard', 'Mouse', 'Monitor', 'Printer', 'External Hard Drive',
        // Food
        'Organic Coffee', 'Premium Tea', 'Chocolate Bar', 'Granola', 'Dried Fruits', 'Nuts', 'Pasta', 
        'Cookies', 'Chips', 'Energy Bars', 'Spices', 'Honey', 'Jam', 'Olive Oil', 'Protein Powder',
        // Cosmetics
        'Face Cream', 'Shampoo', 'Perfume', 'Lipstick', 'Foundation', 'Face Mask', 'Serum', 
        'Body Lotion', 'Sunscreen', 'Hair Oil', 'Face Wash', 'Hand Cream', 'Eye Shadow', 'Mascara', 'Nail Polish',
        // Clothing
        'T-shirt', 'Jeans', 'Dress', 'Sweater', 'Jacket', 'Socks', 'Underwear', 'Scarf', 
        'Gloves', 'Hat', 'Shoes', 'Belt', 'Bag', 'Swimwear', 'Activewear',
        // Toys
        'Action Figure', 'Board Game', 'Puzzle', 'Stuffed Animal', 'Building Blocks', 'Art Set', 
        'Remote Control Car', 'Educational Toy', 'Doll', 'Card Game'
    ];

    productList.forEach(product => {
        let category;
        if (product.match(/(Smartphone|Laptop|Tablet|Camera|Gaming|Power|Router|Keyboard|Mouse|Monitor|Printer|Drive|Headphones|Speaker|Smartwatch)/i)) {
            category = 'electronics';
        } else if (product.match(/(Coffee|Tea|Chocolate|Granola|Fruits|Nuts|Pasta|Cookies|Chips|Bars|Spices|Honey|Jam|Oil|Powder)/i)) {
            category = 'food';
        } else if (product.match(/(Cream|Shampoo|Perfume|Lipstick|Foundation|Mask|Serum|Lotion|Sunscreen|Oil|Wash|Shadow|Mascara|Polish)/i)) {
            category = 'cosmetics';
        } else if (product.match(/(shirt|Jeans|Dress|Sweater|Jacket|Socks|Underwear|Scarf|Gloves|Hat|Shoes|Belt|Bag|Swimwear|Activewear)/i)) {
            category = 'clothing';
        } else {
            category = 'toys';
        }

        const baseCategory = productCategories[category];
        const ecoScoreRange = baseCategory.baseEcoScore;
        
        // Select appropriate packaging material based on category and product characteristics
        let recommendedMaterial;
        switch(category) {
            case 'electronics':
                recommendedMaterial = Math.random() > 0.7 ? 'Recycled PET' : 'Cardboard';
                break;
            case 'food':
                recommendedMaterial = Math.random() > 0.6 ? 'Biodegradable Plastic' : 'Glass';
                break;
            case 'cosmetics':
                recommendedMaterial = Math.random() > 0.5 ? 'Glass' : 'Aluminum';
                break;
            case 'clothing':
                recommendedMaterial = Math.random() > 0.8 ? 'Hemp-based' : 'Recycled PET';
                break;
            case 'toys':
                recommendedMaterial = Math.random() > 0.7 ? 'Cardboard' : 'Recycled PET';
                break;
        }

        const materialData = packagingMaterials[recommendedMaterial];

        products[product.toLowerCase()] = {
            name: product,
            category: category,
            recommended: recommendedMaterial,
            ecoScore: Math.floor(Math.random() * (ecoScoreRange[1] - ecoScoreRange[0]) + ecoScoreRange[0]),
            sustainability: {
                'Recycled PET': Math.floor(Math.random() * 30 + 65),
                'Cardboard': Math.floor(Math.random() * 30 + 65),
                'Biodegradable Plastic': Math.floor(Math.random() * 30 + 65),
                'Glass': Math.floor(Math.random() * 30 + 65),
                'Aluminum': Math.floor(Math.random() * 30 + 65),
                'Hemp-based': Math.floor(Math.random() * 30 + 65),
                'Mushroom Packaging': Math.floor(Math.random() * 30 + 65)
            },
            costs: {
                'Material Cost': Math.floor(materialData.baseCost * (Math.random() * 0.4 + 0.8)),
                'Production Cost': Math.floor(Math.random() * 30 + 60),
                'Transportation Cost': Math.floor(Math.random() * 30 + 60),
                'Recycling Cost': Math.floor(Math.random() * 30 + 60)
            },
            impact: {
                'Carbon Footprint': Math.floor(Math.random() * 30 + 10),
                'Water Usage': Math.floor(Math.random() * 30 + 10),
                'Energy Consumption': Math.floor(Math.random() * 30 + 10),
                'Waste Generation': Math.floor(Math.random() * 30 + 10)
            },
            properties: {
                'Durability': `${materialData.durability}/10`,
                'Water Resistance': `${materialData.waterResistance}/10`,
                'Cost Efficiency': `${Math.floor(Math.random() * 3 + 7)}/10`,
                'Recyclability': `${materialData.recyclability}/10`
            }
        };
    });

    return products;
};

const productDatabase = generateProductDatabase();