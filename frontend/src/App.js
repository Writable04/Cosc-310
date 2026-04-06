import { useCallback, useEffect, useMemo, useState } from "react";
import "./App.css";

const API_BASE_URL = "http://localhost:8000";

const fallbackRestaurants = [
  {
    id: "1",
    name: "Pizza Paradise",
    cuisine: "Italian",
    rating: 4.8,
    deliveryTime: "25-35 min",
    deliveryFee: 2.99,
    description: "Authentic Italian pizza with fresh ingredients.",
    image:
      "https://images.unsplash.com/photo-1513104890138-7c749659a591?auto=format&fit=crop&w=900&q=80",
  },
  {
    id: "2",
    name: "Burger Boss",
    cuisine: "American",
    rating: 4.6,
    deliveryTime: "20-30 min",
    deliveryFee: 1.99,
    description: "Juicy burgers, crispy fries, and late-night comfort food.",
    image:
      "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?auto=format&fit=crop&w=900&q=80",
  },
  {
    id: "3",
    name: "Sushi Supreme",
    cuisine: "Japanese",
    rating: 4.9,
    deliveryTime: "30-40 min",
    deliveryFee: 3.99,
    description: "Fresh sushi platters and beautifully balanced rolls.",
    image:
      "https://images.unsplash.com/photo-1579871494447-9811cf80d66c?auto=format&fit=crop&w=900&q=80",
  },
  {
    id: "4",
    name: "Green Garden",
    cuisine: "Healthy",
    rating: 4.5,
    deliveryTime: "20-30 min",
    deliveryFee: 1.49,
    description: "Colorful bowls, salads, and lighter feel-good meals.",
    image:
      "https://images.unsplash.com/photo-1547592180-85f173990554?auto=format&fit=crop&w=900&q=80",
  },
];

const cuisineImageMap = {
  american:
    "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?auto=format&fit=crop&w=900&q=80",
  asian:
    "https://images.unsplash.com/photo-1512058564366-18510be2db19?auto=format&fit=crop&w=900&q=80",
  bbq:
    "https://images.unsplash.com/photo-1529193591184-b1d58069ecdd?auto=format&fit=crop&w=900&q=80",
  breakfast:
    "https://images.unsplash.com/photo-1525351484163-7529414344d8?auto=format&fit=crop&w=900&q=80",
  canadian:
    "https://images.unsplash.com/photo-1544025162-d76694265947?auto=format&fit=crop&w=900&q=80",
  chinese:
    "https://images.unsplash.com/photo-1585032226651-759b368d7246?auto=format&fit=crop&w=900&q=80",
  healthy:
    "https://images.unsplash.com/photo-1547592180-85f173990554?auto=format&fit=crop&w=900&q=80",
  indian:
    "https://images.unsplash.com/photo-1585937421612-70a008356fbe?auto=format&fit=crop&w=900&q=80",
  italian:
    "https://images.unsplash.com/photo-1513104890138-7c749659a591?auto=format&fit=crop&w=900&q=80",
  japanese:
    "https://images.unsplash.com/photo-1579871494447-9811cf80d66c?auto=format&fit=crop&w=900&q=80",
  mediterranean:
    "https://images.unsplash.com/photo-1547592166-23ac45744acd?auto=format&fit=crop&w=900&q=80",
  mexican:
    "https://images.unsplash.com/photo-1552332386-f8dd00dc2f85?auto=format&fit=crop&w=900&q=80",
  mexico:
    "https://images.unsplash.com/photo-1552332386-f8dd00dc2f85?auto=format&fit=crop&w=900&q=80",
  "middle eastern":
    "https://images.unsplash.com/photo-1541518763669-27fef9dff5bf?auto=format&fit=crop&w=900&q=80",
  seafood:
    "https://images.unsplash.com/photo-1559737558-2f5a35f4523b?auto=format&fit=crop&w=900&q=80",
  thai:
    "https://images.unsplash.com/photo-1559847844-5315695dadae?auto=format&fit=crop&w=900&q=80",
  vegan:
    "https://images.unsplash.com/photo-1512621776951-a57141f2eefd?auto=format&fit=crop&w=900&q=80",
};

function normalizeRestaurants(payload) {
  if (Array.isArray(payload)) {
    return payload;
  }

  if (Array.isArray(payload?.restaurants)) {
    return payload.restaurants;
  }

  if (Array.isArray(payload?.data)) {
    return payload.data;
  }

  return [];
}

function getCuisineImage(cuisine) {
  const normalizedCuisine = (cuisine || "").toLowerCase().trim();
  return cuisineImageMap[normalizedCuisine] || fallbackRestaurants[0].image;
}

function getComboItemCounts(comboItems = []) {
  const counts = new Map();

  comboItems.forEach((itemId) => {
    counts.set(itemId, (counts.get(itemId) || 0) + 1);
  });

  return counts;
}

function mapRestaurant(restaurant) {
  return {
    id: restaurant.id || restaurant.restaurant_id || restaurant.name,
    name: restaurant.name || "Restaurant",
    cuisine: restaurant.cuisine || "Other",
    rating: Number(restaurant.rating || 0),
    deliveryTime: restaurant.deliveryTime
      || (restaurant.durationMinutes ? `${restaurant.durationMinutes} min` : "25-35 min"),
    deliveryFee: Number(restaurant.deliveryFee || 0),
    description:
      restaurant.description
      || restaurant.restaurantAddress
      || "Fresh meals prepared quickly and delivered with care.",
    image: restaurant.image || getCuisineImage(restaurant.cuisine),
    distanceKM: restaurant.distanceKM,
    restaurantAddress: restaurant.restaurantAddress,
  };
}

function mapMenuItem(item) {
  return {
    id: item.item_id || item.id,
    name: item.name || "Menu item",
    price: Number(item.price || 0),
    menuId: item.menu_id,
  };
}

function App() {
  const [username, setUsername] = useState("");
  const [token, setToken] = useState("");
  const [userProfile, setUserProfile] = useState({
    username: "",
    email: "",
    role: "",
    address: "",
  });
  const [authMode, setAuthMode] = useState("login");
  const [draftUsername, setDraftUsername] = useState("");
  const [draftPassword, setDraftPassword] = useState("");
  const [draftConfirmPassword, setDraftConfirmPassword] = useState("");
  const [draftEmail, setDraftEmail] = useState("");
  const [draftRole, setDraftRole] = useState("admin");
  const [draftAddress, setDraftAddress] = useState("");
  const [data, setData] = useState(null);
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedCuisine, setSelectedCuisine] = useState("All");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const [hasLoadedLiveData, setHasLoadedLiveData] = useState(false);
  const [showAuthGate, setShowAuthGate] = useState(true);
  const [selectedRestaurant, setSelectedRestaurant] = useState(null);
  const [restaurantMenu, setRestaurantMenu] = useState(null);
  const [menuItems, setMenuItems] = useState([]);
  const [menuError, setMenuError] = useState("");
  const [isMenuLoading, setIsMenuLoading] = useState(false);
  const [cart, setCart] = useState(null);
  const [cartError, setCartError] = useState("");
  const [cartNotice, setCartNotice] = useState("");
  const [pendingCartKey, setPendingCartKey] = useState("");
  const [showCart, setShowCart] = useState(false);
  const [showAccountMenu, setShowAccountMenu] = useState(false);

  const fetchedRestaurants = useMemo(
    () => normalizeRestaurants(data).map(mapRestaurant),
    [data]
  );
  const restaurants = useMemo(
    () => (hasLoadedLiveData ? fetchedRestaurants : []),
    [fetchedRestaurants, hasLoadedLiveData]
  );

  const cuisines = useMemo(() => {
    const mappedCuisines = restaurants
      .map((restaurant) => restaurant.cuisine || "Other")
      .filter(Boolean);

    return ["All", ...new Set(mappedCuisines)];
  }, [restaurants]);

  const filteredRestaurants = useMemo(() => {
    return restaurants.filter((restaurant) => {
      const name = (restaurant.name || "").toLowerCase();
      const cuisine = (restaurant.cuisine || "Other").toLowerCase();
      const description = (restaurant.description || "").toLowerCase();
      const query = searchTerm.toLowerCase();

      const matchesSearch =
        !query ||
        name.includes(query) ||
        cuisine.includes(query) ||
        description.includes(query);

      const matchesCuisine =
        selectedCuisine === "All" ||
        (restaurant.cuisine || "Other") === selectedCuisine;

      return matchesSearch && matchesCuisine;
    });
  }, [restaurants, searchTerm, selectedCuisine]);

  const fetchRestaurants = useCallback(async ({ useFilters = false, nextUsername, nextToken } = {}) => {
    const activeUsername = (nextUsername ?? username).trim();
    const activeToken = (nextToken ?? token).trim();

    if (!activeUsername || !activeToken) {
      setError("Enter both a username and token before fetching restaurants.");
      return false;
    }

    setIsLoading(true);
    setError("");

    try {
      const cleanUsername = encodeURIComponent(activeUsername);
      const cleanToken = encodeURIComponent(activeToken);
      let url = `${API_BASE_URL}/dataset/restaurants/${cleanUsername}/${cleanToken}`;

      if (useFilters) {
        const params = new URLSearchParams();

        if (searchTerm.trim()) {
          params.set("name", searchTerm.trim());
        }

        if (selectedCuisine !== "All") {
          params.set("cuisine", selectedCuisine);
        }

        url = `${API_BASE_URL}/filters/resturants/${cleanUsername}/${cleanToken}`;
        if (params.toString()) {
          url = `${url}?${params.toString()}`;
        }
      }

      const response = await fetch(url);

      if (!response.ok) {
        throw new Error(`Request failed with status ${response.status}`);
      }

      const payload = await response.json();
      setData(payload);
      setHasLoadedLiveData(true);
      setShowAuthGate(false);
      return true;
    } catch (err) {
      console.error(err);
      setError("We couldn't load restaurants with that username and token. Please try again.");
      setData(null);
      setHasLoadedLiveData(false);
      return false;
    } finally {
      setIsLoading(false);
    }
  }, [searchTerm, selectedCuisine, token, username]);

  const handleSubmit = async () => {
    const nextUsername = draftUsername.trim();
    const nextPassword = draftPassword.trim();

    if (!nextUsername || !nextPassword) {
      setError("Enter your username and password to continue.");
      return;
    }

    setIsLoading(true);
    setError("");

    let nextToken = "";

    try {
      let authUrl = `${API_BASE_URL}/authentication/login/${encodeURIComponent(nextUsername)}`;
      const authParams = new URLSearchParams({
        password: nextPassword,
      });

      if (authMode === "register") {
        if (!draftConfirmPassword.trim() || !draftEmail.trim()) {
          throw new Error("Enter a confirmed password and email to create a user.");
        }

        authUrl = `${API_BASE_URL}/authentication/register/${encodeURIComponent(nextUsername)}`;
        authParams.set("validatated_password", draftConfirmPassword.trim());
        authParams.set("role", draftRole);
        authParams.set("email", draftEmail.trim());

        if (draftAddress.trim()) {
          authParams.set("address", draftAddress.trim());
        }
      }

      const authResponse = await fetch(`${authUrl}?${authParams.toString()}`, {
        method: "POST",
      });

      if (!authResponse.ok) {
        const authPayload = await authResponse.json().catch(() => null);
        const detail = authPayload?.detail || `Authentication failed with status ${authResponse.status}`;
        throw new Error(detail);
      }

      const authPayload = await authResponse.json();
      nextToken = authPayload.token;
    } catch (err) {
      console.error(err);
      setError(err.message || "Authentication failed.");
      setIsLoading(false);
      return;
    }

    const didLoad = await fetchRestaurants({
      useFilters: Boolean(searchTerm.trim()) || selectedCuisine !== "All",
      nextUsername,
      nextToken,
    });

    if (didLoad) {
      setUsername(nextUsername);
      setToken(nextToken);
      setDraftUsername(nextUsername);
      setDraftPassword("");
      setDraftConfirmPassword("");
      setDraftEmail(authMode === "register" ? draftEmail.trim() : draftEmail);

      const cleanUsername = encodeURIComponent(nextUsername);
      const cleanToken = encodeURIComponent(nextToken);

      try {
        try {
          await refreshProfile(nextUsername, nextToken);
        } catch (profileError) {
          console.error(profileError);
          setUserProfile({
            username: nextUsername,
            email: authMode === "register" ? draftEmail.trim() : "",
            role: authMode === "register" ? draftRole : "",
            address: authMode === "register" ? draftAddress.trim() : "",
          });
        }

        const cartResponse = await fetch(`${API_BASE_URL}/cart/${cleanUsername}/${cleanToken}`);

        if (!cartResponse.ok) {
          throw new Error(`Cart request failed with status ${cartResponse.status}`);
        }

        const cartPayload = await cartResponse.json();
        setCart(cartPayload);
        setCartError("");
      } catch (err) {
        console.error(err);
        setCartError("We loaded restaurants, but couldn't load the cart.");
      }
    } else {
      setToken("");
    }
  };

  const handleChangeAccount = () => {
    setShowAccountMenu(false);
    setAuthMode("login");
    setDraftUsername(username);
    setDraftPassword("");
    setDraftConfirmPassword("");
    setDraftEmail("");
    setDraftRole("admin");
    setDraftAddress("");
    setShowAuthGate(true);
    setError("");
  };

  const handleAuthGateBack = () => {
    if (hasLoadedLiveData) {
      setDraftUsername(username);
      setDraftPassword("");
      setDraftConfirmPassword("");
      setDraftEmail("");
      setDraftRole("admin");
      setDraftAddress("");
      setAuthMode("login");
      setShowAuthGate(false);
      setShowAccountMenu(false);
      setError("");
    }
  };

  const refreshProfile = useCallback(async (nextUsername = username, nextToken = token) => {
    const cleanUsername = encodeURIComponent(nextUsername.trim());
    const cleanToken = encodeURIComponent(nextToken.trim());
    const response = await fetch(
      `${API_BASE_URL}/authentication/account/${cleanUsername}/${cleanToken}`
    );

    if (!response.ok) {
      throw new Error(`Profile request failed with status ${response.status}`);
    }

    const profilePayload = await response.json();
    setUserProfile({
      username: nextUsername,
      email: profilePayload.email || "",
      role: profilePayload.role || "",
      address: profilePayload.address || "",
    });
    return profilePayload;
  }, [token, username]);

  const refreshCart = useCallback(async () => {
    const cleanUsername = encodeURIComponent(username.trim());
    const cleanToken = encodeURIComponent(token.trim());
    const cartResponse = await fetch(`${API_BASE_URL}/cart/${cleanUsername}/${cleanToken}`);

    if (!cartResponse.ok) {
      throw new Error(`Cart request failed with status ${cartResponse.status}`);
    }

    const cartPayload = await cartResponse.json();
    setCart(cartPayload);
    return cartPayload;
  }, [token, username]);

  const handleRestaurantSelect = useCallback(async (restaurant) => {
    if (!username.trim() || !token.trim()) {
      return;
    }

    setSelectedRestaurant(restaurant);
    setRestaurantMenu(null);
    setMenuItems([]);
    setMenuError("");
    setIsMenuLoading(true);

    const cleanUsername = encodeURIComponent(username.trim());
    const cleanToken = encodeURIComponent(token.trim());
    const restaurantId = restaurant.id;

    try {
      const restaurantResponse = await fetch(
        `${API_BASE_URL}/dataset/restaurant/${restaurantId}/${cleanUsername}/${cleanToken}`
      );

      if (!restaurantResponse.ok) {
        throw new Error(`Restaurant request failed with status ${restaurantResponse.status}`);
      }

      const restaurantPayload = await restaurantResponse.json();
      const mappedRestaurant = mapRestaurant(restaurantPayload);
      setSelectedRestaurant(mappedRestaurant);

      const menuResponse = await fetch(
        `${API_BASE_URL}/dataset/menu/${restaurantId}`
      );

      if (!menuResponse.ok) {
        if (menuResponse.status === 500 || menuResponse.status === 404) {
          setMenuError("This restaurant doesn't currently have a menu available through the backend.");
          return;
        }

        throw new Error(`Menu request failed with status ${menuResponse.status}`);
      }

      const menuPayload = await menuResponse.json();
      setRestaurantMenu(menuPayload);

      const itemIds = Array.isArray(menuPayload.items) ? menuPayload.items : [];
      const itemResults = await Promise.all(
        itemIds.map(async (itemId) => {
          const itemResponse = await fetch(
            `${API_BASE_URL}/dataset/item/${itemId}/${cleanUsername}/${cleanToken}`
          );

          if (!itemResponse.ok) {
            return null;
          }

          return itemResponse.json();
        })
      );

      setMenuItems(itemResults.filter(Boolean).map(mapMenuItem));
    } catch (err) {
      console.error(err);
      setMenuError("We couldn't load this restaurant's menu right now.");
    } finally {
      setIsMenuLoading(false);
    }
  }, [token, username]);

  const handleCloseRestaurant = () => {
    setSelectedRestaurant(null);
    setRestaurantMenu(null);
    setMenuItems([]);
    setMenuError("");
    setIsMenuLoading(false);
  };

  const comboItemsById = useMemo(() => {
    const itemMap = new Map();

    menuItems.forEach((item) => {
      itemMap.set(item.id, item);
    });

    return itemMap;
  }, [menuItems]);

  const handleAddItemToCart = useCallback(async (item) => {
    const requestKey = `item-${item.id}`;
    setPendingCartKey(requestKey);
    setCartError("");
    setCartNotice("");

    try {
      const cleanUsername = encodeURIComponent(username.trim());
      const cleanToken = encodeURIComponent(token.trim());
      const response = await fetch(
        `${API_BASE_URL}/cart/item/${cleanUsername}/${item.id}/${cleanToken}`,
        { method: "POST" }
      );

      if (!response.ok) {
        throw new Error(`Add item request failed with status ${response.status}`);
      }

      await refreshCart();
      setCartNotice(`${item.name} added to cart.`);
    } catch (err) {
      console.error(err);
      setCartError(`We couldn't add ${item.name} to the cart.`);
    } finally {
      setPendingCartKey("");
    }
  }, [refreshCart, token, username]);

  const handleAddComboToCart = useCallback(async (combo) => {
    const requestKey = `combo-${combo.combo_id}`;
    setPendingCartKey(requestKey);
    setCartError("");
    setCartNotice("");

    try {
      const cleanUsername = encodeURIComponent(username.trim());
      const cleanToken = encodeURIComponent(token.trim());
      const params = new URLSearchParams({
        combo_id: String(combo.combo_id),
        menu_id: String(combo.menu_id || restaurantMenu?.menu_id || selectedRestaurant?.id),
      });

      const response = await fetch(
        `${API_BASE_URL}/cart/combo/${cleanUsername}/${combo.combo_id}/${cleanToken}?${params.toString()}`,
        {
          method: "POST",
        }
      );

      if (!response.ok) {
        throw new Error(`Add combo request failed with status ${response.status}`);
      }

      const cartPayload = await response.json();
      setCart(cartPayload);
      setCartNotice(`Combo #${combo.combo_id} added to cart.`);
    } catch (err) {
      console.error(err);
      setCartError(`We couldn't add combo #${combo.combo_id} to the cart.`);
    } finally {
      setPendingCartKey("");
    }
  }, [restaurantMenu, selectedRestaurant, token, username]);

  const handleCartQuantityChange = useCallback(async (cartItem, delta) => {
    const requestKey = `cart-item-${cartItem.itemID}-${delta}`;
    setPendingCartKey(requestKey);
    setCartError("");
    setCartNotice("");

    try {
      const cleanUsername = encodeURIComponent(username.trim());
      const cleanToken = encodeURIComponent(token.trim());

      if (delta > 0) {
        const response = await fetch(
          `${API_BASE_URL}/cart/item/${cleanUsername}/${cartItem.itemID}/${cleanToken}`,
          { method: "POST" }
        );

        if (!response.ok) {
          throw new Error(`Increase item request failed with status ${response.status}`);
        }
      } else {
        const response = await fetch(
          `${API_BASE_URL}/cart/item/${cleanUsername}/${cartItem.itemID}/${cleanToken}`,
          { method: "DELETE" }
        );

        if (!response.ok) {
          throw new Error(`Decrease item request failed with status ${response.status}`);
        }
      }

      await refreshCart();
    } catch (err) {
      console.error(err);
      setCartError(`We couldn't update ${cartItem.name} in the cart.`);
    } finally {
      setPendingCartKey("");
    }
  }, [refreshCart, token, username]);

  const handleRemoveCartItem = useCallback(async (cartItem) => {
    const requestKey = `cart-remove-${cartItem.itemID}`;
    setPendingCartKey(requestKey);
    setCartError("");
    setCartNotice("");

    try {
      const cleanUsername = encodeURIComponent(username.trim());
      const cleanToken = encodeURIComponent(token.trim());

      for (let count = 0; count < Number(cartItem.quantity || 0); count += 1) {
        const response = await fetch(
          `${API_BASE_URL}/cart/item/${cleanUsername}/${cartItem.itemID}/${cleanToken}`,
          { method: "DELETE" }
        );

        if (!response.ok) {
          throw new Error(`Remove item request failed with status ${response.status}`);
        }
      }

      await refreshCart();
      setCartNotice(`${cartItem.name} removed from cart.`);
    } catch (err) {
      console.error(err);
      setCartError(`We couldn't remove ${cartItem.name} from the cart.`);
    } finally {
      setPendingCartKey("");
    }
  }, [refreshCart, token, username]);

  const handleRemoveCombo = useCallback(async (combo) => {
    const requestKey = `combo-remove-${combo.combo_id}`;
    setPendingCartKey(requestKey);
    setCartError("");
    setCartNotice("");

    try {
      const cleanUsername = encodeURIComponent(username.trim());
      const cleanToken = encodeURIComponent(token.trim());
      const response = await fetch(
        `${API_BASE_URL}/cart/combo/${cleanUsername}/${combo.combo_id}/${cleanToken}`,
        { method: "DELETE" }
      );

      if (!response.ok) {
        throw new Error(`Remove combo request failed with status ${response.status}`);
      }

      await refreshCart();
      setCartNotice(`Combo #${combo.combo_id} removed from cart.`);
    } catch (err) {
      console.error(err);
      setCartError(`We couldn't remove combo #${combo.combo_id} from the cart.`);
    } finally {
      setPendingCartKey("");
    }
  }, [refreshCart, token, username]);

  const handleComboQuantityChange = useCallback(async (combo, delta) => {
    const requestKey = `combo-${combo.combo_id}-${delta}`;
    setPendingCartKey(requestKey);
    setCartError("");
    setCartNotice("");

    try {
      const cleanUsername = encodeURIComponent(username.trim());
      const cleanToken = encodeURIComponent(token.trim());

      if (delta > 0) {
        const comboMenuItemId = combo.comboItems?.[0];

        if (!comboMenuItemId) {
          throw new Error("Combo does not include any items.");
        }

        const itemResponse = await fetch(
          `${API_BASE_URL}/dataset/item/${comboMenuItemId}/${cleanUsername}/${cleanToken}`
        );

        if (!itemResponse.ok) {
          throw new Error(`Combo item lookup failed with status ${itemResponse.status}`);
        }

        const itemPayload = await itemResponse.json();
        const params = new URLSearchParams({
          menu_id: String(itemPayload.menu_id),
        });

        const response = await fetch(
          `${API_BASE_URL}/cart/combo/${cleanUsername}/${combo.combo_id}/${cleanToken}?${params.toString()}`,
          { method: "POST" }
        );

        if (!response.ok) {
          throw new Error(`Increase combo request failed with status ${response.status}`);
        }
      } else {
        const response = await fetch(
          `${API_BASE_URL}/cart/combo/${cleanUsername}/${combo.combo_id}/${cleanToken}`,
          { method: "DELETE" }
        );

        if (!response.ok) {
          throw new Error(`Decrease combo request failed with status ${response.status}`);
        }
      }

      await refreshCart();
    } catch (err) {
      console.error(err);
      setCartError(`We couldn't update combo #${combo.combo_id}.`);
    } finally {
      setPendingCartKey("");
    }
  }, [refreshCart, token, username]);

  const totalCartItems = useMemo(() => {
    return (cart?.items || []).reduce((sum, item) => sum + Number(item.quantity || 0), 0);
  }, [cart]);

  const cartDisplayEntries = useMemo(() => {
    if (!cart) {
      return [];
    }

    const itemNameMap = new Map((cart.items || []).map((item) => [item.itemID, item.name]));
    const coveredCounts = new Map();

    (cart.appliedCombos || []).forEach((combo) => {
      const comboItemCounts = getComboItemCounts(combo.comboItems);

      comboItemCounts.forEach((count, itemId) => {
        const totalCovered = count * Number(combo.quantity || 0);
        coveredCounts.set(itemId, (coveredCounts.get(itemId) || 0) + totalCovered);
      });
    });

    const comboEntries = (cart.appliedCombos || []).map((combo, index) => ({
      key: `combo-${combo.combo_id}-${index}`,
      type: "combo",
      combo,
      quantity: Number(combo.quantity || 0),
      title: `Combo #${combo.combo_id}`,
      subtitle: combo.comboItems
        .map((itemId) => itemNameMap.get(itemId) || `Item ${itemId}`)
        .join(", "),
      value: `-$${Number(combo.discountPrice || 0).toFixed(2)} off`,
    }));

    const itemEntries = (cart.items || [])
      .map((item) => {
        const remainingQuantity = Number(item.quantity || 0) - (coveredCounts.get(item.itemID) || 0);

        if (remainingQuantity <= 0) {
          return null;
        }

        return {
          key: `item-${item.itemID}`,
          type: "item",
          item: {
            ...item,
            quantity: remainingQuantity,
          },
          quantity: remainingQuantity,
          title: item.name,
          subtitle: `$${Number(item.price || 0).toFixed(2)} each`,
          value: `$${Number(item.price || 0).toFixed(2)}`,
        };
      })
      .filter(Boolean);

    return [...comboEntries, ...itemEntries];
  }, [cart]);

  const backendStatusLabel = hasLoadedLiveData ? "Backend online" : "Backend offline";
  const profileInitial = (userProfile.username || username || "U").charAt(0).toUpperCase();

  useEffect(() => {
    if (!hasLoadedLiveData) {
      return;
    }

    const timeoutId = window.setTimeout(() => {
      fetchRestaurants({
        useFilters: Boolean(searchTerm.trim()) || selectedCuisine !== "All",
      });
    }, 300);

    return () => window.clearTimeout(timeoutId);
  }, [fetchRestaurants, hasLoadedLiveData, searchTerm, selectedCuisine]);

  return (
    <div className="app-shell">
      {showAuthGate ? (
        <div className="auth-gate">
          <div className="auth-card">
            <p className="panel-label">Connect your dataset</p>
            <h2>{authMode === "login" ? "Login to your account" : "Create a new user"}</h2>
            <p className="panel-copy">
              Choose how you want to enter the app, then we&apos;ll load your restaurant data automatically.
            </p>

            <div className="auth-mode-switch">
              <button
                type="button"
                className={authMode === "login" ? "auth-mode-chip active" : "auth-mode-chip"}
                onClick={() => {
                  setAuthMode("login");
                  setError("");
                }}
              >
                Login
              </button>
              <button
                type="button"
                className={authMode === "register" ? "auth-mode-chip active" : "auth-mode-chip"}
                onClick={() => {
                  setAuthMode("register");
                  setError("");
                }}
              >
                Create user
              </button>
            </div>

            <label>
              Username
              <input
                type="text"
                placeholder="Enter username"
                value={draftUsername}
                onChange={(e) => setDraftUsername(e.target.value)}
              />
            </label>

            <label>
              Password
              <input
                type="password"
                placeholder={authMode === "login" ? "Enter password" : "Create password"}
                value={draftPassword}
                onChange={(e) => setDraftPassword(e.target.value)}
              />
            </label>

            {authMode === "register" ? (
              <>
                <label>
                  Confirm password
                  <input
                    type="password"
                    placeholder="Re-enter password"
                    value={draftConfirmPassword}
                    onChange={(e) => setDraftConfirmPassword(e.target.value)}
                  />
                </label>

                <label>
                  Email
                  <input
                    type="email"
                    placeholder="Enter email"
                    value={draftEmail}
                    onChange={(e) => setDraftEmail(e.target.value)}
                  />
                </label>

                <label>
                  Role
                  <select
                    value={draftRole}
                    onChange={(e) => setDraftRole(e.target.value)}
                    className="auth-select"
                  >
                    <option value="admin">Admin</option>
                    <option value="manager">Manager</option>
                    <option value="user">User</option>
                  </select>
                </label>

                <label>
                  Address
                  <input
                    type="text"
                    placeholder="Optional address"
                    value={draftAddress}
                    onChange={(e) => setDraftAddress(e.target.value)}
                  />
                </label>
              </>
            ) : null}

            <div className="auth-actions">
              <button
                type="button"
                className="auth-secondary"
                onClick={handleAuthGateBack}
                disabled={!hasLoadedLiveData || isLoading}
              >
                Back
              </button>
              <button onClick={handleSubmit} disabled={isLoading}>
                {isLoading
                  ? authMode === "login"
                    ? "Logging in..."
                    : "Creating user..."
                  : authMode === "login"
                    ? "Login"
                    : "Create user"}
              </button>
            </div>

            <div className="panel-status">
              <p>
                {authMode === "login"
                  ? "We’ll log in first, then fetch your restaurants."
                  : "We’ll create your user, return a token, and then fetch your restaurants."}
              </p>
              {error ? <p>{error}</p> : null}
            </div>
          </div>
        </div>
      ) : null}

      <header className="topbar">
        <div className="brand-lockup">
          <div className="brand-mark">Q</div>
          <div>
            <p className="brand-kicker">Food Delivery</p>
            <h1>QuickEats</h1>
          </div>
        </div>
        <div className="topbar-copy">
          {hasLoadedLiveData ? (
            <span className={hasLoadedLiveData ? "backend-status online" : "backend-status offline"}>
              {backendStatusLabel}
            </span>
          ) : null}
          {hasLoadedLiveData ? (
            <div className="header-actions">
              <button className="header-pill" onClick={() => setShowCart(true)} type="button">
                <span>Cart</span>
                <strong>{totalCartItems}</strong>
              </button>
              <div className="account-menu-wrap">
                <button
                  className="profile-button"
                  onClick={() => setShowAccountMenu((open) => !open)}
                  type="button"
                  aria-label="Open profile menu"
                >
                  <span>{profileInitial}</span>
                </button>
                {showAccountMenu ? (
                  <div className="account-menu profile-menu">
                    <div className="profile-summary">
                      <div className="profile-avatar-large">{profileInitial}</div>
                      <div>
                        <p className="profile-name">{userProfile.username || username}</p>
                        <p className="profile-meta">
                          {userProfile.email || "Email unavailable"}
                        </p>
                      </div>
                    </div>
                    <div className="profile-details">
                      <p>
                        <span>Role</span>
                        <strong>{userProfile.role || "Unavailable"}</strong>
                      </p>
                      <p>
                        <span>Address</span>
                        <strong>{userProfile.address || "Unavailable"}</strong>
                      </p>
                      <p>
                        <span>Backend</span>
                        <strong>{backendStatusLabel}</strong>
                      </p>
                    </div>
                    <button className="account-menu-item" onClick={handleChangeAccount} type="button">
                      Change login
                    </button>
                  </div>
                ) : null}
              </div>
            </div>
          ) : null}
          {!hasLoadedLiveData ? (
            <span className={hasLoadedLiveData ? "backend-status online" : "backend-status offline"}>
            {backendStatusLabel}
            </span>
          ) : null}
        </div>
      </header>

      <main>
        <section className="hero">
          <div className="hero-copy">
            
            <h2>Order delivery near you.</h2>
            <p className="hero-text">
              
            </p>

            <div className="hero-search">
              <span className="search-icon">Search</span>
              <input
                type="text"
                placeholder="Search restaurants, cuisines, or dishes"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                disabled={!hasLoadedLiveData}
              />
            </div>

            <div className="hero-stats">
              <div>
                <strong>{restaurants.length}</strong>
                <span>Restaurants</span>
              </div>
              <div>
                <strong>15 min</strong>
                <span>Avg pickup</span>
              </div>
              <div>
                <strong>4.8/5</strong>
                <span>Top rated</span>
              </div>
            </div>
          </div>
        </section>

        {(cartNotice || cartError || error) && hasLoadedLiveData ? (
          <section className="status-strip">
            {cartNotice ? <p className="cart-success">{cartNotice}</p> : null}
            {cartError ? <p className="cart-error">{cartError}</p> : null}
            {error ? <p className="cart-error">{error}</p> : null}
          </section>
        ) : null}

        <section className="filters-section">
          <div className="section-heading">
            <div>
              <p className="eyebrow">Browse restaurants</p>
              <h3>{filteredRestaurants.length} places available right now</h3>
            </div>
            <p className="section-copy">
              Filter by cuisine or use the search bar to narrow the list.
            </p>
          </div>

          <div className="cuisine-row">
            {cuisines.map((cuisine) => (
              <button
                key={cuisine}
                type="button"
                className={selectedCuisine === cuisine ? "chip active" : "chip"}
                onClick={() => setSelectedCuisine(cuisine)}
              >
                {cuisine}
              </button>
            ))}
          </div>
        </section>

        <section className="restaurant-grid">
          {filteredRestaurants.map((restaurant, index) => (
            <article
              className="restaurant-card"
              key={restaurant.id || index}
              onClick={() => handleRestaurantSelect(restaurant)}
              onKeyDown={(event) => {
                if (event.key === "Enter" || event.key === " ") {
                  event.preventDefault();
                  handleRestaurantSelect(restaurant);
                }
              }}
              role="button"
              tabIndex={0}
            >
              <div
                className="restaurant-media"
                style={{
                  backgroundImage: `linear-gradient(180deg, rgba(18, 23, 34, 0.02), rgba(18, 23, 34, 0.45)), url(${restaurant.image})`,
                }}
              >
                <span className="rating-badge">
                  {restaurant.rating || "4.7"} rating
                </span>
              </div>

              <div className="restaurant-body">
                <div className="restaurant-header">
                  <div>
                    <h4>{restaurant.name || "Restaurant"}</h4>
                    <p>{restaurant.cuisine || "Cuisine"}</p>
                  </div>
                  <span className="delivery-fee">
                    ${Number(restaurant.deliveryFee || 0).toFixed(2)}
                  </span>
                </div>

                <p className="restaurant-description">
                  {restaurant.description ||
                    "Fresh meals prepared quickly and delivered with care."}
                </p>

                <div className="restaurant-meta">
                  <span>{restaurant.deliveryTime || "25-35 min"}</span>
                  <span>
                    {restaurant.distanceKM
                      ? `${restaurant.distanceKM} km away`
                      : "Minimum order friendly"}
                  </span>
                </div>
              </div>
            </article>
          ))}
        </section>

        {!filteredRestaurants.length ? (
          <section className="empty-state">
            <h3>No restaurants matched your filters.</h3>
            <p>Try another cuisine or clear the search term.</p>
          </section>
        ) : null}

        <section className="data-panel">
          <div className="section-heading">
            <div>
              <p className="eyebrow">API preview</p>
              <h3>Current response payload</h3>
            </div>
            <p className="section-copy">
              This stays visible so you can still inspect what the backend is returning.
            </p>
          </div>
          <pre>{JSON.stringify(data, null, 2) || "No live payload loaded yet."}</pre>
        </section>

        {selectedRestaurant ? (
          <section className="detail-overlay" onClick={handleCloseRestaurant}>
            <div
              className="detail-panel"
              onClick={(event) => event.stopPropagation()}
              role="dialog"
              aria-modal="true"
            >
              <div className="detail-header">
                <div>
                  <p className="eyebrow">Restaurant details</p>
                  <h3>{selectedRestaurant.name}</h3>
                  <p className="section-copy">
                    {selectedRestaurant.cuisine} · {selectedRestaurant.restaurantAddress || "Address unavailable"}
                  </p>
                </div>
                <button className="ghost-action" onClick={handleCloseRestaurant} type="button">
                  Close
                </button>
              </div>

              {isMenuLoading ? (
                <div className="detail-state">
                  <p>Loading menu items and combos...</p>
                </div>
              ) : null}

              {!isMenuLoading && menuError ? (
                <div className="detail-state">
                  <p>{menuError}</p>
                </div>
              ) : null}

              {!isMenuLoading && !menuError ? (
                <div className="detail-content">
                  <div className="detail-section">
                    <div className="detail-section-header">
                      <h4>Menu Items</h4>
                      <span>{menuItems.length} loaded</span>
                    </div>
                    {menuItems.length ? (
                      <div className="menu-list">
                        {menuItems.map((item) => (
                          <article className="menu-card" key={item.id}>
                            <div>
                              <h5>{item.name}</h5>
                              <p>Item ID: {item.id}</p>
                            </div>
                            <div className="menu-actions">
                              <strong>${item.price.toFixed(2)}</strong>
                              <button
                                type="button"
                                className="inline-action"
                                onClick={() => handleAddItemToCart(item)}
                                disabled={pendingCartKey === `item-${item.id}`}
                              >
                                {pendingCartKey === `item-${item.id}` ? "Adding..." : "Add to cart"}
                              </button>
                            </div>
                          </article>
                        ))}
                      </div>
                    ) : (
                      <p className="detail-empty">No menu items were returned.</p>
                    )}
                  </div>

                  <div className="detail-section">
                    <div className="detail-section-header">
                      <h4>Combos</h4>
                      <span>{restaurantMenu?.menuCombos?.length || 0} available</span>
                    </div>
                    {restaurantMenu?.menuCombos?.length ? (
                      <div className="combo-list">
                        {restaurantMenu.menuCombos.map((combo, index) => (
                          <article className="combo-card" key={`${combo.combo_id}-${index}`}>
                            <div className="combo-topline">
                              <h5>Combo #{combo.combo_id}</h5>
                              <div className="menu-actions">
                                <strong>${Number(combo.discountPrice || 0).toFixed(2)} off</strong>
                                <button
                                  type="button"
                                  className="inline-action"
                                  onClick={() => handleAddComboToCart(combo)}
                                  disabled={pendingCartKey === `combo-${combo.combo_id}`}
                                >
                                  {pendingCartKey === `combo-${combo.combo_id}` ? "Adding..." : "Add combo"}
                                </button>
                              </div>
                            </div>
                            <p>
                              Includes: {combo.comboItems
                                .map((itemId) => comboItemsById.get(itemId)?.name || `Item ${itemId}`)
                                .join(", ")}
                            </p>
                          </article>
                        ))}
                      </div>
                    ) : (
                      <p className="detail-empty">No combos were returned for this menu.</p>
                    )}
                  </div>
                </div>
              ) : null}

              {cart ? (
                <div className="detail-cart-bar">
                  <p>{cart.restaurant || selectedRestaurant.name}</p>
                  <p>{cart.items?.length || 0} item lines</p>
                  <p>${Number(cart.checkout_total || 0).toFixed(2)} total</p>
                </div>
              ) : null}
            </div>
          </section>
        ) : null}

        {showCart ? (
          <section className="detail-overlay" onClick={() => setShowCart(false)}>
            <div
              className="cart-panel"
              onClick={(event) => event.stopPropagation()}
              role="dialog"
              aria-modal="true"
            >
              <div className="detail-header">
                <div>
                  <p className="eyebrow">Your cart</p>
                  <h3>{cart?.restaurant || "Current order"}</h3>
                  <p className="section-copy">
                    Edit item quantities and remove items from your order.
                  </p>
                </div>
                <div className="cart-header-actions">
                  <button className="ghost-action" onClick={() => setShowCart(false)} type="button">
                    Close
                  </button>
                </div>
              </div>

              {cartError ? <div className="detail-state"><p>{cartError}</p></div> : null}
              {cartNotice ? <div className="detail-state cart-state-success"><p>{cartNotice}</p></div> : null}

              <div className="cart-modal-grid">
                <div className="detail-section">
                  <div className="detail-section-header">
                    <h4>Cart</h4>
                    <span>{cartDisplayEntries.length} lines</span>
                  </div>
                  {cartDisplayEntries.length ? (
                    <div className="menu-list">
                      {cartDisplayEntries.map((entry) => (
                        <article className="cart-item-card" key={entry.key}>
                          <div>
                            <h5>{entry.title}</h5>
                            <p>{entry.subtitle}</p>
                          </div>
                          <div className="cart-item-actions">
                            <div className="qty-editor">
                              <button
                                type="button"
                                className="qty-button"
                                onClick={() => (
                                  entry.type === "combo"
                                    ? handleComboQuantityChange(entry.combo, -1)
                                    : handleCartQuantityChange(entry.item, -1)
                                )}
                                disabled={
                                  entry.type === "combo"
                                    ? pendingCartKey === `combo-${entry.combo.combo_id}--1`
                                    : pendingCartKey === `cart-item-${entry.item.itemID}--1`
                                }
                              >
                                -
                              </button>
                              <span>{entry.quantity}</span>
                              <button
                                type="button"
                                className="qty-button"
                                onClick={() => (
                                  entry.type === "combo"
                                    ? handleComboQuantityChange(entry.combo, 1)
                                    : handleCartQuantityChange(entry.item, 1)
                                )}
                                disabled={
                                  entry.type === "combo"
                                    ? pendingCartKey === `combo-${entry.combo.combo_id}-1`
                                    : pendingCartKey === `cart-item-${entry.item.itemID}-1`
                                }
                              >
                                +
                              </button>
                            </div>
                            <span className="cart-line-value">{entry.value}</span>
                            <button
                              type="button"
                              className="inline-action inline-action-muted"
                              onClick={() => (
                                entry.type === "combo"
                                  ? handleRemoveCombo(entry.combo)
                                  : handleRemoveCartItem(entry.item)
                              )}
                              disabled={
                                entry.type === "combo"
                                  ? pendingCartKey === `combo-remove-${entry.combo.combo_id}`
                                  : pendingCartKey === `cart-remove-${entry.item.itemID}`
                              }
                            >
                              {entry.type === "combo"
                                ? pendingCartKey === `combo-remove-${entry.combo.combo_id}`
                                  ? "Removing..."
                                  : "Remove"
                                : pendingCartKey === `cart-remove-${entry.item.itemID}`
                                  ? "Removing..."
                                  : "Remove"}
                            </button>
                          </div>
                        </article>
                      ))}
                    </div>
                  ) : (
                    <p className="detail-empty">Your cart is empty.</p>
                  )}
                </div>

                <div className="detail-section">
                  <div className="detail-section-header">
                    <h4>Summary</h4>
                    <span>${Number(cart?.checkout_total || 0).toFixed(2)}</span>
                  </div>
                  <div className="cart-breakdown">
                    <p>Subtotal</p>
                    <strong>${Number(cart?.subtotal || 0).toFixed(2)}</strong>
                    <p>Discount</p>
                    <strong>${Number(cart?.totalDiscount || 0).toFixed(2)}</strong>
                    <p>Total</p>
                    <strong>${Number(cart?.checkout_total || 0).toFixed(2)}</strong>
                  </div>
                </div>
              </div>
            </div>
          </section>
        ) : null}
      </main>
    </div>
  );
}

export default App;
