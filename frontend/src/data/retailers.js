/**
 * List of supported retailers in Kenya for Thamani
 */
export const retailers = [
  {
    id: 1,
    name: "Jumia Kenya",
    website: "https://www.jumia.co.ke/",
    logo: "/retailers/jumia.png",
    description: "Kenya's largest online marketplace",
    categories: ["Electronics", "Fashion", "Home & Kitchen", "Beauty", "Phones", "Computing"],
    isPopular: true
  },
  {
    id: 2,
    name: "Kilimall",
    website: "https://www.kilimall.co.ke/",
    logo: "/retailers/kilimall.png",
    description: "Online shopping mall with a wide range of products",
    categories: ["Electronics", "Fashion", "Home & Living", "Phones", "Computing"],
    isPopular: true
  },
  {
    id: 3,
    name: "Masoko",
    website: "https://www.masoko.com/",
    logo: "/retailers/masoko.png",
    description: "Safaricom's online marketplace",
    categories: ["Electronics", "Home & Office", "Phones", "Computing"],
    isPopular: true
  },
  {
    id: 4,
    name: "Jiji Kenya",
    website: "https://jiji.co.ke/",
    logo: "/retailers/jiji.png",
    description: "Classifieds marketplace for new and used items",
    categories: ["Electronics", "Vehicles", "Real Estate", "Furniture", "Fashion"],
    isPopular: true
  },
  {
    id: 5,
    name: "Carrefour Kenya",
    website: "https://www.carrefour.ke/",
    logo: "/retailers/carrefour.png",
    description: "Supermarket chain with online shopping",
    categories: ["Groceries", "Home & Kitchen", "Electronics", "Appliances"],
    isPopular: true
  },
  {
    id: 6,
    name: "Naivas Online",
    website: "https://www.naivas.co.ke/",
    logo: "/retailers/naivas.png",
    description: "Kenya's leading supermarket chain",
    categories: ["Groceries", "Home & Kitchen", "Electronics"],
    isPopular: true
  },
  {
    id: 7,
    name: "Electrohub",
    website: "https://electrohub.co.ke/",
    logo: "/retailers/electrohub.png",
    description: "Specialized electronics retailer",
    categories: ["Electronics", "Phones", "Computing", "Appliances"],
    isPopular: false
  },
  {
    id: 8,
    name: "Avechi",
    website: "https://www.avechi.com/",
    logo: "/retailers/avechi.png",
    description: "Online electronics store",
    categories: ["Electronics", "Phones", "Computing", "Cameras"],
    isPopular: false
  },
  {
    id: 9,
    name: "Copia Kenya",
    website: "https://copia.co.ke/",
    logo: "/retailers/copia.png",
    description: "E-commerce platform serving urban and rural consumers",
    categories: ["Groceries", "Home & Kitchen", "Electronics", "Personal Care"],
    isPopular: false
  },
  {
    id: 10,
    name: "SkyGarden",
    website: "https://sky.garden/",
    logo: "/retailers/skygarden.png",
    description: "Marketplace for various Kenyan businesses",
    categories: ["Fashion", "Electronics", "Home & Living", "Health & Beauty"],
    isPopular: false
  },
  {
    id: 11,
    name: "Opalnet",
    website: "https://www.opalnet.co.ke/",
    logo: "/retailers/opalnet.png",
    description: "Computer hardware and electronics retailer",
    categories: ["Computing", "Electronics", "Networking", "Office Equipment"],
    isPopular: false
  },
  {
    id: 12,
    name: "Shopit",
    website: "https://shopit.co.ke/",
    logo: "/retailers/shopit.png",
    description: "Online shopping platform for various products",
    categories: ["Electronics", "Home & Kitchen", "Fashion", "Beauty"],
    isPopular: false
  }
];

/**
 * Get popular retailers
 * @returns {Array} Array of popular retailers
 */
export const getPopularRetailers = () => {
  return retailers.filter(retailer => retailer.isPopular);
};

/**
 * Get retailers by category
 * @param {string} category - Category to filter by
 * @returns {Array} Array of retailers that sell products in the specified category
 */
export const getRetailersByCategory = (category) => {
  return retailers.filter(retailer => 
    retailer.categories.includes(category)
  );
};

/**
 * Get all unique categories across all retailers
 * @returns {Array} Array of unique categories
 */
export const getAllCategories = () => {
  const categoriesSet = new Set();
  
  retailers.forEach(retailer => {
    retailer.categories.forEach(category => {
      categoriesSet.add(category);
    });
  });
  
  return Array.from(categoriesSet).sort();
};

export default retailers;
