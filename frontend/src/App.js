import { useCallback, useEffect, useMemo, useState } from "react";
import "./App.css";

const API_BASE_URL = "http://localhost:8000";
const CREATE_RESTAURANT_OPTION = "__create_new_restaurant__";

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
    restaurant_id: restaurant.restaurant_id || restaurant.id,
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
    owner: restaurant.owner || "",
    distanceKM: restaurant.distanceKM,
    restaurantAddress: restaurant.restaurantAddress,
  };
}

function mapMenuItem(item) {
  return {
    id: item.item_id || item.id,
    item_id: item.item_id || item.id,
    name: item.name || "Menu item",
    price: Number(item.price || 0),
    menuId: item.menu_id,
  };
}

function normalizeRole(role) {
  return String(role || "").trim().toLowerCase();
}

function parseNumberList(rawValue) {
  return String(rawValue || "")
    .split(",")
    .map((value) => Number(value.trim()))
    .filter((value) => Number.isFinite(value));
}

function serializeNumberList(values) {
  return Array.isArray(values) ? values.join(", ") : "";
}

function parseComboConfig(rawValue, menuId) {
  if (!String(rawValue || "").trim()) {
    return [];
  }

  const parsed = JSON.parse(rawValue);
  if (!Array.isArray(parsed)) {
    throw new Error("Combos must be a JSON array.");
  }

  return parsed.map((combo) => ({
    combo_id: Number(combo.combo_id),
    comboItems: Array.isArray(combo.comboItems) ? combo.comboItems.map(Number) : [],
    discountPrice: Number(combo.discountPrice || 0),
    menu_id: Number(combo.menu_id || menuId),
  }));
}

function serializeComboConfig(combos) {
  if (!Array.isArray(combos) || !combos.length) {
    return "";
  }

  return JSON.stringify(combos, null, 2);
}

function emptyRestaurantForm() {
  return {
    restaurant_id: "",
    name: "",
    cuisine: "",
    rating: "0",
    restaurantAddress: "",
    owner: "",
  };
}

function emptyMenuForm() {
  return {
    itemsText: "",
    combosText: "",
  };
}

function emptyItemForm(menuId = "") {
  return {
    item_id: "0",
    name: "",
    price: "",
    menu_id: menuId ? String(menuId) : "",
  };
}

function emptyComboForm() {
  return {
    combo_id: "",
    comboItemsText: "",
    discountPrice: "0",
  };
}

function mapCombo(combo) {
  return {
    combo_id: Number(combo.combo_id || 0),
    comboItems: Array.isArray(combo.comboItems) ? combo.comboItems.map(Number) : [],
    discountPrice: Number(combo.discountPrice || 0),
    menu_id: Number(combo.menu_id || 0),
  };
}

function emptyPaymentForm() {
  return {
    card_holder_name: "",
    card_number: "",
    expiry_month: "",
    expiry_year: "",
    cvv: "",
    card_type: "credit",
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
  const [authNotice, setAuthNotice] = useState("");
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
  const [showFavourites, setShowFavourites] = useState(false);
  const [favouriteRestaurants, setFavouriteRestaurants] = useState([]);
  const [isFavouritesLoading, setIsFavouritesLoading] = useState(false);
  const [favouritesError, setFavouritesError] = useState("");
  const [favouritesNotice, setFavouritesNotice] = useState("");
  const [pendingFavouriteRestaurantId, setPendingFavouriteRestaurantId] = useState("");
  const [showCheckout, setShowCheckout] = useState(false);
  const [checkoutError, setCheckoutError] = useState("");
  const [checkoutNotice, setCheckoutNotice] = useState("");
  const [isCheckoutLoading, setIsCheckoutLoading] = useState(false);
  const [savedPaymentMethods, setSavedPaymentMethods] = useState([]);
  const [checkoutMethodMode, setCheckoutMethodMode] = useState("saved");
  const [selectedPaymentMethodId, setSelectedPaymentMethodId] = useState("");
  const [paymentForm, setPaymentForm] = useState(emptyPaymentForm);
  const [savePaymentMethod, setSavePaymentMethod] = useState(false);
  const [checkoutResult, setCheckoutResult] = useState(null);
  const [checkoutOrderSummary, setCheckoutOrderSummary] = useState(null);
  const [showAccountMenu, setShowAccountMenu] = useState(false);
  const [showManagementPanel, setShowManagementPanel] = useState(false);
  const [managementRestaurantId, setManagementRestaurantId] = useState("");
  const [isCreatingManagementRestaurant, setIsCreatingManagementRestaurant] = useState(false);
  const [managementNotice, setManagementNotice] = useState("");
  const [managementError, setManagementError] = useState("");
  const [isManagementLoading, setIsManagementLoading] = useState(false);
  const [managementMenuExists, setManagementMenuExists] = useState(false);
  const [managementRestaurants, setManagementRestaurants] = useState([]);
  const [managementItems, setManagementItems] = useState([]);
  const [managementCombos, setManagementCombos] = useState([]);
  const [restaurantForm, setRestaurantForm] = useState(emptyRestaurantForm);
  const [menuForm, setMenuForm] = useState(emptyMenuForm);
  const [itemForm, setItemForm] = useState(emptyItemForm);
  const [comboForm, setComboForm] = useState(emptyComboForm);

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
    setAuthNotice("");

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
        authParams.set("address", draftAddress.trim());
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
      if (authMode === "register") {
        setAuthNotice("User created successfully. Loading restaurant data now.");
      }
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
      setDraftAddress(authMode === "register" ? draftAddress.trim() : draftAddress);

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
        try {
          await refreshFavourites();
        } catch (favouritesLoadError) {
          console.error(favouritesLoadError);
        }
      } catch (err) {
        console.error(err);
        setCartError("We loaded restaurants, but couldn't load the cart.");
      }
    } else {
      if (authMode === "register") {
        setAuthNotice("User created successfully, but the restaurant data could not be loaded yet. Try logging in with the new account.");
      }
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
    setAuthNotice("");
    setShowFavourites(false);
    setFavouriteRestaurants([]);
    setFavouritesError("");
    setFavouritesNotice("");
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
      setAuthNotice("");
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

  const refreshFavourites = useCallback(async () => {
    const cleanUsername = encodeURIComponent(username.trim());
    const cleanToken = encodeURIComponent(token.trim());
    const response = await fetch(`${API_BASE_URL}/favourites/${cleanUsername}/${cleanToken}`);

    if (!response.ok) {
      throw new Error(`Favourites request failed with status ${response.status}`);
    }

    const payload = await response.json();
    const nextRestaurants = Array.isArray(payload?.restaurant_ids)
      ? payload.restaurant_ids.filter(Boolean).map(mapRestaurant)
      : [];

    setFavouriteRestaurants(nextRestaurants);
    return nextRestaurants;
  }, [token, username]);

  const loadPaymentMethods = useCallback(async () => {
    const cleanUsername = encodeURIComponent(username.trim());
    const response = await fetch(`${API_BASE_URL}/payment/methods?username=${cleanUsername}`);

    if (!response.ok) {
      throw new Error(`Payment methods request failed with status ${response.status}`);
    }

    const payload = await response.json();
    const methods = Array.isArray(payload) ? payload : [];
    setSavedPaymentMethods(methods);

    const defaultMethod = methods.find((method) => method.is_default);
    const fallbackMethod = methods[0];
    const nextMethodId = defaultMethod?.method_id || fallbackMethod?.method_id || "";
    setSelectedPaymentMethodId(nextMethodId);
    setCheckoutMethodMode(nextMethodId ? "saved" : "new");
    return methods;
  }, [username]);

  const openFavouritesPanel = useCallback(async () => {
    setShowFavourites(true);
    setShowAccountMenu(false);
    setFavouritesError("");
    setFavouritesNotice("");
    setIsFavouritesLoading(true);

    try {
      await refreshFavourites();
    } catch (err) {
      console.error(err);
      setFavouritesError("We couldn't load your favourite restaurants.");
    } finally {
      setIsFavouritesLoading(false);
    }
  }, [refreshFavourites]);

  const openCheckoutPanel = useCallback(async () => {
    if (!username.trim() || !token.trim()) {
      setCheckoutError("Log in before checking out.");
      return;
    }

    setCheckoutError("");
    setCheckoutNotice("");
    setCheckoutResult(null);
    setCheckoutOrderSummary(null);
    setPaymentForm(emptyPaymentForm());
    setSavePaymentMethod(false);
    setShowCheckout(true);
    setIsCheckoutLoading(true);

    try {
      const latestCart = await refreshCart();
      if (!latestCart?.items?.length) {
        setCheckoutError("Your cart is empty. Add items before checking out.");
        return;
      }

      await loadPaymentMethods();
    } catch (err) {
      console.error(err);
      setCheckoutError("We couldn't load checkout details right now.");
    } finally {
      setIsCheckoutLoading(false);
    }
  }, [loadPaymentMethods, refreshCart, token, username]);

  const handleCloseCheckout = useCallback(() => {
    setShowCheckout(false);
    setCheckoutError("");
    setCheckoutNotice("");
    setCheckoutResult(null);
    setCheckoutOrderSummary(null);
    setIsCheckoutLoading(false);
  }, []);

  const handleCheckoutSubmit = useCallback(async () => {
    if (!cart?.items?.length) {
      setCheckoutError("Your cart is empty. Add items before checking out.");
      return;
    }

    if (checkoutMethodMode === "saved" && !selectedPaymentMethodId) {
      setCheckoutError("Choose a saved payment method or switch to a new card.");
      return;
    }

    if (checkoutMethodMode === "new") {
      const requiredFields = [
        paymentForm.card_holder_name,
        paymentForm.card_number,
        paymentForm.expiry_month,
        paymentForm.expiry_year,
        paymentForm.cvv,
      ];

      if (requiredFields.some((value) => !String(value || "").trim())) {
        setCheckoutError("Complete all card fields before checking out.");
        return;
      }
    }

    setCheckoutError("");
    setCheckoutNotice("");
    setIsCheckoutLoading(true);

    try {
      const cleanUsername = encodeURIComponent(username.trim());
      const cleanToken = encodeURIComponent(token.trim());

      let checkoutBody = {};

      if (checkoutMethodMode === "saved") {
        checkoutBody = { method_id: selectedPaymentMethodId };
      } else {
        const nextMethod = {
          card_holder_name: paymentForm.card_holder_name.trim(),
          card_number: paymentForm.card_number.trim(),
          expiry_month: Number(paymentForm.expiry_month),
          expiry_year: Number(paymentForm.expiry_year),
          cvv: paymentForm.cvv.trim(),
          card_type: paymentForm.card_type,
        };

        if (savePaymentMethod) {
          const saveResponse = await fetch(`${API_BASE_URL}/payment/methods?username=${cleanUsername}`, {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify(nextMethod),
          });

          if (!saveResponse.ok) {
            const failure = await saveResponse.json().catch(() => null);
            throw new Error(failure?.detail || `Save payment method failed with status ${saveResponse.status}`);
          }

          const savedMethod = await saveResponse.json();
          checkoutBody = { method_id: savedMethod.method_id };
          await loadPaymentMethods();
        } else {
          checkoutBody = { new_method: nextMethod };
        }
      }

      const checkoutResponse = await fetch(`${API_BASE_URL}/checkout/${cleanUsername}/${cleanToken}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(checkoutBody),
      });

      if (!checkoutResponse.ok) {
        const failure = await checkoutResponse.json().catch(() => null);
        throw new Error(failure?.detail || `Checkout failed with status ${checkoutResponse.status}`);
      }

      const checkoutPayload = await checkoutResponse.json();
      setCheckoutResult(checkoutPayload);
      setCheckoutNotice(checkoutPayload.message || "Checkout completed successfully.");

      if (checkoutPayload.order_id) {
        const summaryResponse = await fetch(
          `${API_BASE_URL}/delivery/${checkoutPayload.order_id}/summary?username=${cleanUsername}&token=${cleanToken}`
        );

        if (summaryResponse.ok) {
          const summaryPayload = await summaryResponse.json();
          setCheckoutOrderSummary(summaryPayload);
        }
      }

      const clearResponse = await fetch(`${API_BASE_URL}/cart/${cleanUsername}/${cleanToken}`, {
        method: "PUT",
      });

      if (clearResponse.ok) {
        const clearedCart = await clearResponse.json();
        setCart(clearedCart);
      } else {
        await refreshCart();
      }
    } catch (err) {
      console.error(err);
      setCheckoutError(err.message || "We couldn't complete checkout.");
    } finally {
      setIsCheckoutLoading(false);
    }
  }, [cart, checkoutMethodMode, loadPaymentMethods, paymentForm, refreshCart, savePaymentMethod, selectedPaymentMethodId, token, username]);

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

  const favouriteRestaurantIds = useMemo(() => {
    return new Set(
      favouriteRestaurants.map((restaurant) => String(restaurant.restaurant_id || restaurant.id))
    );
  }, [favouriteRestaurants]);

  const isRestaurantFavourite = useCallback((restaurantId) => {
    return favouriteRestaurantIds.has(String(restaurantId));
  }, [favouriteRestaurantIds]);

  const handleToggleFavouriteRestaurant = useCallback(async (restaurant) => {
    const restaurantId = restaurant?.restaurant_id || restaurant?.id;
    if (!restaurantId) {
      return;
    }

    const requestKey = String(restaurantId);
    setPendingFavouriteRestaurantId(requestKey);
    setFavouritesError("");
    setFavouritesNotice("");

    try {
      const cleanUsername = encodeURIComponent(username.trim());
      const cleanToken = encodeURIComponent(token.trim());
      const isFavourite = isRestaurantFavourite(restaurantId);
      const response = await fetch(
        `${API_BASE_URL}/favourites/restaurant/${restaurantId}/${cleanUsername}/${cleanToken}`,
        {
          method: isFavourite ? "DELETE" : "POST",
        }
      );

      if (!response.ok) {
        const failure = await response.json().catch(() => null);
        throw new Error(failure?.detail || `Favourite request failed with status ${response.status}`);
      }

      await refreshFavourites();
      setFavouritesNotice(
        isFavourite
          ? `${restaurant.name} removed from favourites.`
          : `${restaurant.name} added to favourites.`
      );
    } catch (err) {
      console.error(err);
      setFavouritesError("We couldn't update favourites right now.");
    } finally {
      setPendingFavouriteRestaurantId("");
    }
  }, [isRestaurantFavourite, refreshFavourites, token, username]);

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
  const normalizedRole = normalizeRole(userProfile.role);
  const canManageCatalog = normalizedRole === "manager" || normalizedRole === "admin";
  const canManageAllCatalog = normalizedRole === "admin";
  const refreshManagementCatalog = useCallback(async () => {
    const [restaurantsResponse, itemsResponse, combosResponse] = await Promise.all([
      fetch(`${API_BASE_URL}/dataset/restaurants`),
      fetch(`${API_BASE_URL}/dataset/items`),
      fetch(`${API_BASE_URL}/cart/combos`),
    ]);

    if (!restaurantsResponse.ok) {
      throw new Error(`Restaurants dataset failed with status ${restaurantsResponse.status}`);
    }

    if (!itemsResponse.ok) {
      throw new Error(`Items dataset failed with status ${itemsResponse.status}`);
    }

    if (!combosResponse.ok) {
      throw new Error(`Combos dataset failed with status ${combosResponse.status}`);
    }

    const [restaurantsPayload, itemsPayload, combosPayload] = await Promise.all([
      restaurantsResponse.json(),
      itemsResponse.json(),
      combosResponse.json(),
    ]);

    const mappedRestaurants = Array.isArray(restaurantsPayload)
      ? restaurantsPayload.map(mapRestaurant)
      : [];
    const mappedItems = Array.isArray(itemsPayload)
      ? itemsPayload.map(mapMenuItem)
      : [];
    const mappedCombos = Array.isArray(combosPayload)
      ? combosPayload.map(mapCombo)
      : [];

    setManagementRestaurants(mappedRestaurants);
    setManagementItems(mappedItems);
    setManagementCombos(mappedCombos);

    return {
      restaurants: mappedRestaurants,
      items: mappedItems,
      combos: mappedCombos,
    };
  }, []);

  const manageableRestaurants = useMemo(() => {
    if (canManageAllCatalog) {
      return managementRestaurants;
    }

    return managementRestaurants.filter((restaurant) => normalizeRole(restaurant.owner) === normalizeRole(username));
  }, [canManageAllCatalog, managementRestaurants, username]);

  const selectedManagedRestaurant = useMemo(() => {
    return managementRestaurants.find(
      (restaurant) => String(restaurant.restaurant_id || restaurant.id) === String(managementRestaurantId)
    ) || null;
  }, [managementRestaurantId, managementRestaurants]);
  const hasManagementContext = Boolean(managementRestaurantId) || isCreatingManagementRestaurant;
  const managementSelectValue = isCreatingManagementRestaurant
    ? CREATE_RESTAURANT_OPTION
    : managementRestaurantId;
  const currentManagementCombos = useMemo(() => {
    const menuId = Number(managementRestaurantId || 0);
    return managementCombos.filter((combo) => Number(combo.menu_id) === menuId);
  }, [managementCombos, managementRestaurantId]);

  const loadManagementRestaurantData = useCallback(async (restaurantId = managementRestaurantId) => {
    if (!restaurantId || !username.trim() || !token.trim()) {
      return;
    }

    const catalog = await refreshManagementCatalog();
    const cleanUsername = encodeURIComponent(username.trim());
    const cleanToken = encodeURIComponent(token.trim());
    const restaurantResponse = await fetch(
      `${API_BASE_URL}/dataset/restaurant/${restaurantId}/${cleanUsername}/${cleanToken}`
    );

    if (!restaurantResponse.ok) {
      throw new Error(`Restaurant request failed with status ${restaurantResponse.status}`);
    }

    const restaurantPayload = await restaurantResponse.json();
    setRestaurantForm({
      restaurant_id: String(restaurantPayload.restaurant_id || restaurantId),
      name: restaurantPayload.name || "",
      cuisine: restaurantPayload.cuisine || "",
      rating: String(restaurantPayload.rating ?? 0),
      restaurantAddress: restaurantPayload.restaurantAddress || "",
      owner: restaurantPayload.owner || "",
    });

    const scopedItems = catalog.items.filter((item) => Number(item.menuId) === Number(restaurantId));
    const scopedCombos = catalog.combos.filter((combo) => Number(combo.menu_id) === Number(restaurantId));
    const menuResponse = await fetch(`${API_BASE_URL}/dataset/menu/${restaurantId}`);
    if (menuResponse.ok) {
      setManagementMenuExists(true);
      setMenuForm({
        itemsText: serializeNumberList(scopedItems.map((item) => item.item_id)),
        combosText: serializeComboConfig(scopedCombos),
      });
      setMenuItems(scopedItems);
      setItemForm((current) => ({
        ...current,
        menu_id: String(restaurantId),
      }));
    } else if (scopedItems.length || scopedCombos.length) {
      setManagementMenuExists(false);
      setMenuForm({
        itemsText: serializeNumberList(scopedItems.map((item) => item.item_id)),
        combosText: serializeComboConfig(scopedCombos),
      });
      setMenuItems(scopedItems);
      setItemForm((current) => ({
        ...current,
        menu_id: String(restaurantId),
      }));
    } else {
      setManagementMenuExists(false);
      setMenuForm({
        itemsText: "",
        combosText: "",
      });
      setMenuItems([]);
      setItemForm(emptyItemForm(String(restaurantId)));
    }
  }, [managementRestaurantId, refreshManagementCatalog, token, username]);

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

  useEffect(() => {
    if (!showManagementPanel || !managementRestaurantId || !username.trim() || !token.trim()) {
      return;
    }

    const loadManagementRestaurant = async () => {
      setIsManagementLoading(true);
      setManagementError("");

      try {
        await loadManagementRestaurantData(managementRestaurantId);
      } catch (err) {
        console.error(err);
        setManagementError("We couldn't load that restaurant into the management panel.");
      } finally {
        setIsManagementLoading(false);
      }
    };

    loadManagementRestaurant();
  }, [loadManagementRestaurantData, managementRestaurantId, showManagementPanel, token, username]);

  const resetManagementForms = useCallback((nextRestaurantId = "") => {
    setManagementMenuExists(false);
    setRestaurantForm(emptyRestaurantForm());
    setMenuForm({
      ...emptyMenuForm(),
    });
    setItemForm(emptyItemForm(nextRestaurantId));
    setComboForm(emptyComboForm());
    setMenuItems([]);
  }, []);

  const persistManagementMenu = useCallback(async (nextMenuForm, successMessage) => {
    const menuId = Number(managementRestaurantId);
    if (!menuId) {
      throw new Error("Select a restaurant first.");
    }

    const cleanUsername = encodeURIComponent(username.trim());
    const cleanToken = encodeURIComponent(token.trim());
    const payload = {
      menu_id: menuId,
      items: parseNumberList(nextMenuForm.itemsText),
      menuCombos: parseComboConfig(nextMenuForm.combosText, menuId),
    };

    const method = managementMenuExists ? "PUT" : "POST";
    const endpoint = method === "PUT"
      ? `${API_BASE_URL}/dataset/menu/${menuId}/${cleanUsername}/${cleanToken}`
      : `${API_BASE_URL}/dataset/menu/${cleanUsername}/${cleanToken}`;
    const response = await fetch(endpoint, {
      method,
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      const failure = await response.json().catch(() => null);
      throw new Error(failure?.detail || `Save menu failed with status ${response.status}`);
    }

    setManagementMenuExists(true);
    setMenuForm(nextMenuForm);
    setManagementNotice(successMessage);
  }, [managementMenuExists, managementRestaurantId, token, username]);

  const openManagementPanel = useCallback(() => {
    setShowManagementPanel(true);
    setShowAccountMenu(false);
    setManagementError("");
    setManagementNotice("");
    refreshManagementCatalog().catch((err) => {
      console.error(err);
      setManagementError("We couldn't load the management datasets.");
    });
    if (!managementRestaurantId && !isCreatingManagementRestaurant) {
      resetManagementForms("");
    }
  }, [isCreatingManagementRestaurant, managementRestaurantId, refreshManagementCatalog, resetManagementForms]);

  const handleManagementRestaurantSelect = useCallback((event) => {
    const nextId = event.target.value;

    if (nextId === CREATE_RESTAURANT_OPTION) {
      setManagementRestaurantId("");
      setIsCreatingManagementRestaurant(true);
      setManagementNotice("");
      setManagementError("");
      resetManagementForms("");
      return;
    }

    setManagementRestaurantId(nextId);
    setIsCreatingManagementRestaurant(false);
    setManagementNotice("");
    setManagementError("");

    if (!nextId) {
      resetManagementForms("");
    }
  }, [resetManagementForms]);

  const handleStartCreateRestaurant = useCallback(() => {
    setManagementRestaurantId("");
    setIsCreatingManagementRestaurant(true);
    setManagementNotice("");
    setManagementError("");
    resetManagementForms("");
  }, [resetManagementForms]);

  const handleCreateRestaurant = useCallback(async () => {
    setManagementError("");
    setManagementNotice("");
    setIsManagementLoading(true);

    try {
      const cleanUsername = encodeURIComponent(username.trim());
      const cleanToken = encodeURIComponent(token.trim());
      const payload = {
        restaurant_id: 0,
        name: restaurantForm.name.trim(),
        cuisine: restaurantForm.cuisine.trim(),
        rating: Number(restaurantForm.rating || 0),
        restaurantAddress: restaurantForm.restaurantAddress.trim(),
        durationMinutes: 0,
        distanceKM: 0,
        owner: canManageAllCatalog ? (restaurantForm.owner.trim() || username.trim()) : username.trim(),
      };

      const response = await fetch(`${API_BASE_URL}/dataset/restaurant/${cleanUsername}/${cleanToken}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        const failure = await response.json().catch(() => null);
        throw new Error(failure?.detail || `Create restaurant failed with status ${response.status}`);
      }

      await fetchRestaurants({
        useFilters: Boolean(searchTerm.trim()) || selectedCuisine !== "All",
      });
      const catalog = await refreshManagementCatalog();
      const match = catalog.restaurants.find((restaurant) => (
        restaurant.name === payload.name
        && restaurant.restaurantAddress === payload.restaurantAddress
      ));

      if (match) {
        setManagementRestaurantId(String(match.restaurant_id || match.id));
      }

      setIsCreatingManagementRestaurant(false);
      setManagementNotice("Restaurant created successfully.");
    } catch (err) {
      console.error(err);
      setManagementError(err.message || "We couldn't create the restaurant.");
    } finally {
      setIsManagementLoading(false);
    }
  }, [canManageAllCatalog, fetchRestaurants, refreshManagementCatalog, restaurantForm, searchTerm, selectedCuisine, token, username]);

  const handleCreateRestaurantAction = useCallback(() => {
    if (isCreatingManagementRestaurant) {
      handleCreateRestaurant();
      return;
    }

    handleStartCreateRestaurant();
  }, [handleCreateRestaurant, handleStartCreateRestaurant, isCreatingManagementRestaurant]);

  const handleUpdateRestaurant = useCallback(async () => {
    if (!managementRestaurantId) {
      setManagementError("Select a restaurant to update first.");
      return;
    }

    setManagementError("");
    setManagementNotice("");
    setIsManagementLoading(true);

    try {
      const cleanUsername = encodeURIComponent(username.trim());
      const cleanToken = encodeURIComponent(token.trim());
      const payload = {
        restaurant_id: Number(managementRestaurantId),
        name: restaurantForm.name.trim(),
        cuisine: restaurantForm.cuisine.trim(),
        rating: Number(restaurantForm.rating || 0),
        restaurantAddress: restaurantForm.restaurantAddress.trim(),
        durationMinutes: 0,
        distanceKM: 0,
        owner: restaurantForm.owner || selectedManagedRestaurant?.owner || "",
      };

      const response = await fetch(
        `${API_BASE_URL}/dataset/restaurant/${managementRestaurantId}/${cleanUsername}/${cleanToken}`,
        {
          method: "PUT",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(payload),
        }
      );

      if (!response.ok) {
        const failure = await response.json().catch(() => null);
        throw new Error(failure?.detail || `Update restaurant failed with status ${response.status}`);
      }

      await fetchRestaurants({
        useFilters: Boolean(searchTerm.trim()) || selectedCuisine !== "All",
      });
      await loadManagementRestaurantData(managementRestaurantId);
      setManagementNotice("Restaurant updated successfully.");
    } catch (err) {
      console.error(err);
      setManagementError(err.message || "We couldn't update the restaurant.");
    } finally {
      setIsManagementLoading(false);
    }
  }, [fetchRestaurants, loadManagementRestaurantData, managementRestaurantId, restaurantForm, searchTerm, selectedCuisine, selectedManagedRestaurant, token, username]);

  const handleDeleteRestaurant = useCallback(async () => {
    if (!managementRestaurantId) {
      setManagementError("Select a restaurant to remove first.");
      return;
    }

    setManagementError("");
    setManagementNotice("");
    setIsManagementLoading(true);

    try {
      const cleanUsername = encodeURIComponent(username.trim());
      const cleanToken = encodeURIComponent(token.trim());

      for (const item of managementItems.filter((entry) => Number(entry.menuId) === Number(managementRestaurantId))) {
        const itemResponse = await fetch(
          `${API_BASE_URL}/dataset/item/${item.item_id}/${cleanUsername}/${cleanToken}`,
          { method: "DELETE" }
        );

        if (!itemResponse.ok) {
          const failure = await itemResponse.json().catch(() => null);
          throw new Error(failure?.detail || `Delete item failed with status ${itemResponse.status}`);
        }
      }

      await fetch(
        `${API_BASE_URL}/dataset/menu/${managementRestaurantId}/${cleanUsername}/${cleanToken}`,
        { method: "DELETE" }
      ).catch(() => null);

      const response = await fetch(
        `${API_BASE_URL}/dataset/restaurant/${managementRestaurantId}/${cleanUsername}/${cleanToken}`,
        {
          method: "DELETE",
        }
      );

      if (!response.ok) {
        const failure = await response.json().catch(() => null);
        throw new Error(failure?.detail || `Delete restaurant failed with status ${response.status}`);
      }

      await fetchRestaurants({
        useFilters: Boolean(searchTerm.trim()) || selectedCuisine !== "All",
      });
      await refreshManagementCatalog();
      setManagementRestaurantId("");
      setIsCreatingManagementRestaurant(false);
      resetManagementForms("");
      setManagementNotice("Restaurant removed successfully.");
    } catch (err) {
      console.error(err);
      setManagementError(err.message || "We couldn't remove the restaurant.");
    } finally {
      setIsManagementLoading(false);
    }
  }, [fetchRestaurants, managementItems, managementRestaurantId, refreshManagementCatalog, resetManagementForms, searchTerm, selectedCuisine, token, username]);

  const handleSaveItem = useCallback(async () => {
    const menuId = Number(managementRestaurantId);
    const requestedItemId = Number(itemForm.item_id || 0);
    const itemId = requestedItemId > 0 ? requestedItemId : 0;
    if (!menuId || !itemForm.name.trim() || !itemForm.price) {
      setManagementError("Item name, price, and a selected restaurant are required.");
      return;
    }

    setManagementError("");
    setManagementNotice("");
    setIsManagementLoading(true);

    try {
      const cleanUsername = encodeURIComponent(username.trim());
      const cleanToken = encodeURIComponent(token.trim());
      const existingItem = itemId > 0
        ? menuItems.find((item) => String(item.item_id) === String(itemId))
        : null;
      const payload = {
        item_id: itemId,
        name: itemForm.name.trim(),
        price: String(itemForm.price).trim(),
        menu_id: menuId,
      };

      const method = existingItem ? "PUT" : "POST";
      const endpoint = existingItem
        ? `${API_BASE_URL}/dataset/item/${itemId}/${cleanUsername}/${cleanToken}`
        : `${API_BASE_URL}/dataset/item/${cleanUsername}/${cleanToken}`;
      const response = await fetch(endpoint, {
        method,
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        const failure = await response.json().catch(() => null);
        throw new Error(failure?.detail || `Save item failed with status ${response.status}`);
      }

      const catalog = await refreshManagementCatalog();
      const scopedItems = catalog.items.filter((item) => Number(item.menuId) === menuId);
      const nextMenuForm = {
        ...menuForm,
        itemsText: serializeNumberList(scopedItems.map((item) => item.item_id)),
      };
      await persistManagementMenu(
        nextMenuForm,
        existingItem ? "Item updated successfully." : "Item created successfully."
      );
      await loadManagementRestaurantData(menuId);
      setItemForm(emptyItemForm(String(menuId)));
    } catch (err) {
      console.error(err);
      setManagementError(err.message || "We couldn't save the item.");
    } finally {
      setIsManagementLoading(false);
    }
  }, [itemForm, loadManagementRestaurantData, managementRestaurantId, menuForm, menuItems, persistManagementMenu, refreshManagementCatalog, token, username]);

  const handleDeleteItem = useCallback(async (itemId) => {
    setManagementError("");
    setManagementNotice("");
    setIsManagementLoading(true);

    try {
      const cleanUsername = encodeURIComponent(username.trim());
      const cleanToken = encodeURIComponent(token.trim());
      const response = await fetch(
        `${API_BASE_URL}/dataset/item/${itemId}/${cleanUsername}/${cleanToken}`,
        { method: "DELETE" }
      );

      if (!response.ok) {
        const failure = await response.json().catch(() => null);
        throw new Error(failure?.detail || `Delete item failed with status ${response.status}`);
      }

      const catalog = await refreshManagementCatalog();
      const scopedItems = catalog.items.filter((item) => Number(item.menuId) === Number(managementRestaurantId));
      const nextMenuForm = {
        ...menuForm,
        itemsText: serializeNumberList(scopedItems.map((item) => item.item_id)),
      };
      await persistManagementMenu(nextMenuForm, "Item removed successfully.");
      await loadManagementRestaurantData(managementRestaurantId);
    } catch (err) {
      console.error(err);
      setManagementError(err.message || "We couldn't remove the item.");
    } finally {
      setIsManagementLoading(false);
    }
  }, [loadManagementRestaurantData, managementRestaurantId, menuForm, persistManagementMenu, refreshManagementCatalog, token, username]);

  const populateItemForm = useCallback((item) => {
    setItemForm({
      item_id: String(item.item_id || item.id),
      name: item.name || "",
      price: String(item.price ?? ""),
      menu_id: String(managementRestaurantId),
    });
    setManagementNotice("");
    setManagementError("");
  }, [managementRestaurantId]);

  const handleSaveCombo = useCallback(async () => {
    const menuId = Number(managementRestaurantId);
    if (!menuId) {
      setManagementError("Select a restaurant first.");
      return;
    }

    if (!comboForm.comboItemsText.trim()) {
      setManagementError("Enter the combo item IDs.");
      return;
    }

    setManagementError("");
    setManagementNotice("");
    setIsManagementLoading(true);

    try {
      const currentCombos = parseComboConfig(menuForm.combosText, menuId);
      const requestedComboId = Number(comboForm.combo_id || 0);
      const existingComboIndex = requestedComboId > 0
        ? currentCombos.findIndex((combo) => combo.combo_id === requestedComboId)
        : -1;
      const nextComboId = existingComboIndex >= 0
        ? requestedComboId
        : managementCombos.reduce((maxId, combo) => Math.max(maxId, Number(combo.combo_id || 0)), 0) + 1;

      const nextCombo = {
        combo_id: nextComboId,
        comboItems: parseNumberList(comboForm.comboItemsText),
        discountPrice: Number(comboForm.discountPrice || 0),
        menu_id: menuId,
      };

      const nextCombos = existingComboIndex >= 0
        ? currentCombos.map((combo, index) => (index === existingComboIndex ? nextCombo : combo))
        : [...currentCombos, nextCombo];

      const nextMenuForm = {
        ...menuForm,
        combosText: serializeComboConfig(nextCombos),
      };

      await persistManagementMenu(
        nextMenuForm,
        existingComboIndex >= 0 ? "Combo updated successfully." : "Combo created successfully."
      );
      await loadManagementRestaurantData(menuId);
      setComboForm(emptyComboForm());
    } catch (err) {
      console.error(err);
      setManagementError(err.message || "We couldn't save the combo.");
    } finally {
      setIsManagementLoading(false);
    }
  }, [comboForm, loadManagementRestaurantData, managementCombos, managementRestaurantId, menuForm, persistManagementMenu]);

  const handleDeleteCombo = useCallback(async (comboId) => {
    const menuId = Number(managementRestaurantId);
    if (!menuId) {
      setManagementError("Select a restaurant first.");
      return;
    }

    setManagementError("");
    setManagementNotice("");
    setIsManagementLoading(true);

    try {
      const currentCombos = parseComboConfig(menuForm.combosText, menuId);
      const nextCombos = currentCombos.filter((combo) => Number(combo.combo_id) !== Number(comboId));
      const nextMenuForm = {
        ...menuForm,
        combosText: serializeComboConfig(nextCombos),
      };
      await persistManagementMenu(nextMenuForm, "Combo removed successfully.");
      await loadManagementRestaurantData(menuId);
      setComboForm((current) => (
        Number(current.combo_id) === Number(comboId) ? emptyComboForm() : current
      ));
    } catch (err) {
      console.error(err);
      setManagementError(err.message || "We couldn't remove the combo.");
    } finally {
      setIsManagementLoading(false);
    }
  }, [loadManagementRestaurantData, managementRestaurantId, menuForm, persistManagementMenu]);

  const populateComboForm = useCallback((combo) => {
    setComboForm({
      combo_id: String(combo.combo_id || 0),
      comboItemsText: serializeNumberList(combo.comboItems),
      discountPrice: String(combo.discountPrice ?? 0),
    });
    setManagementNotice("");
    setManagementError("");
  }, []);

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
                  setAuthNotice("");
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
                  setAuthNotice("");
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
              {authNotice ? <p className="auth-success">{authNotice}</p> : null}
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
              {canManageCatalog ? (
                <button className="header-pill header-pill-admin" onClick={openManagementPanel} type="button">
                  <span>{canManageAllCatalog ? "Admin" : "Manager"}</span>
                  <strong>Manage</strong>
                </button>
              ) : null}
              <button className="header-pill" onClick={openFavouritesPanel} type="button">
                <span>Favorites</span>
                <strong>{favouriteRestaurants.length}</strong>
              </button>
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

        {showManagementPanel ? (
          <section className="detail-overlay" onClick={() => setShowManagementPanel(false)}>
            <div
              className="cart-panel management-panel"
              onClick={(event) => event.stopPropagation()}
              role="dialog"
              aria-modal="true"
            >
              <div className="detail-header">
                <div>
                  <p className="eyebrow">{canManageAllCatalog ? "Admin tools" : "Manager tools"}</p>
                  <h3>{canManageAllCatalog ? "Manage all catalog data" : "Manage your catalog data"}</h3>
                  <p className="section-copy">
                    {canManageAllCatalog
                      ? "Create, edit, and remove any restaurant, menu, or item."
                      : "Create restaurants and manage the restaurants owned by your username."}
                  </p>
                </div>
                <div className="cart-header-actions">
                  <button className="ghost-action" onClick={() => setShowManagementPanel(false)} type="button">
                    Close
                  </button>
                </div>
              </div>

              {managementError ? <div className="detail-state"><p>{managementError}</p></div> : null}
              {managementNotice ? <div className="detail-state cart-state-success"><p>{managementNotice}</p></div> : null}

              <div className="management-grid">
                <div className="detail-section">
                  <div className="detail-section-header">
                    <h4>Restaurant controls</h4>
                    <span>{manageableRestaurants.length} available</span>
                  </div>

                  <label className="management-label">
                    Select editable restaurant
                    <select
                      className="auth-select"
                      value={managementSelectValue}
                      onChange={handleManagementRestaurantSelect}
                    >
                      <option value="">Select a restaurant</option>
                      <option value={CREATE_RESTAURANT_OPTION}>Create new restaurant</option>
                      {manageableRestaurants.map((restaurant) => (
                        <option
                          key={restaurant.restaurant_id || restaurant.id}
                          value={restaurant.restaurant_id || restaurant.id}
                        >
                          {restaurant.name} ({restaurant.owner || "no owner"})
                        </option>
                      ))}
                    </select>
                  </label>

                  <div className="management-form">
                    <label className="management-label">
                      Name
                      <input
                        type="text"
                        value={restaurantForm.name}
                        onChange={(event) => setRestaurantForm((current) => ({ ...current, name: event.target.value }))}
                      />
                    </label>
                    <label className="management-label">
                      Cuisine
                      <input
                        type="text"
                        value={restaurantForm.cuisine}
                        onChange={(event) => setRestaurantForm((current) => ({ ...current, cuisine: event.target.value }))}
                      />
                    </label>
                    <label className="management-label">
                      Rating
                      <input
                        type="number"
                        min="0"
                        max="5"
                        step="0.1"
                        value={restaurantForm.rating}
                        onChange={(event) => setRestaurantForm((current) => ({ ...current, rating: event.target.value }))}
                      />
                    </label>
                    <label className="management-label">
                      Address
                      <input
                        type="text"
                        value={restaurantForm.restaurantAddress}
                        onChange={(event) => setRestaurantForm((current) => ({ ...current, restaurantAddress: event.target.value }))}
                      />
                    </label>
                    <label className="management-label">
                      Owner
                      <input
                        type="text"
                        value={restaurantForm.owner || username}
                        onChange={(event) => setRestaurantForm((current) => ({ ...current, owner: event.target.value }))}
                        disabled={!canManageAllCatalog}
                      />
                    </label>
                  </div>

                  <div className="management-actions">
                    <button className="inline-action" onClick={handleCreateRestaurantAction} type="button" disabled={isManagementLoading}>
                      Create restaurant
                    </button>
                    <button className="inline-action" onClick={handleUpdateRestaurant} type="button" disabled={!managementRestaurantId || isManagementLoading}>
                      Save restaurant
                    </button>
                    <button className="inline-action inline-action-muted" onClick={handleDeleteRestaurant} type="button" disabled={!managementRestaurantId || isManagementLoading}>
                      Remove restaurant
                    </button>
                  </div>
                </div>

                {hasManagementContext ? (
                  <div className="detail-section">
                    <div className="detail-section-header">
                      <h4>Combo controls</h4>
                      <span>{managementRestaurantId ? `Restaurant ${managementRestaurantId}` : "New restaurant"}</span>
                    </div>
                    {!managementRestaurantId ? (
                      <p className="detail-empty">Create the restaurant first, then add combos to it.</p>
                    ) : (
                      <>
                        <div className="management-form">
                          <p className="management-helper">
                            New combos automatically get the next available combo ID.
                          </p>
                          <label className="management-label">
                            Combo item IDs
                            <textarea
                              rows="4"
                              value={comboForm.comboItemsText}
                              onChange={(event) => setComboForm((current) => ({ ...current, comboItemsText: event.target.value }))}
                              placeholder="1, 2, 3"
                            />
                          </label>
                          <label className="management-label">
                            Discount price
                            <input
                              type="number"
                              min="0"
                              step="0.01"
                              value={comboForm.discountPrice}
                              onChange={(event) => setComboForm((current) => ({ ...current, discountPrice: event.target.value }))}
                            />
                          </label>
                        </div>

                        <div className="management-actions">
                          <button className="inline-action" onClick={handleSaveCombo} type="button" disabled={isManagementLoading}>
                            Save combo
                          </button>
                        </div>

                        {currentManagementCombos.length ? (
                          <div className="combo-list management-sublist">
                            {currentManagementCombos.map((combo) => (
                              <article className="combo-card" key={`manage-combo-${combo.combo_id}`}>
                                <div className="combo-topline">
                                  <h5>Combo #{combo.combo_id}</h5>
                                  <div className="menu-actions">
                                    <strong>${Number(combo.discountPrice || 0).toFixed(2)} off</strong>
                                    <button className="inline-action" onClick={() => populateComboForm(combo)} type="button">
                                      Edit
                                    </button>
                                    <button className="inline-action inline-action-muted" onClick={() => handleDeleteCombo(combo.combo_id)} type="button">
                                      Remove
                                    </button>
                                  </div>
                                </div>
                                <p>Includes item IDs: {combo.comboItems.join(", ")}</p>
                              </article>
                            ))}
                          </div>
                        ) : (
                          <p className="detail-empty">No combos for this restaurant yet.</p>
                        )}
                      </>
                    )}
                  </div>
                ) : null}
              </div>

              {hasManagementContext ? (
                <div className="management-grid management-grid-secondary">
                  <div className="detail-section">
                    <div className="detail-section-header">
                      <h4>Item controls</h4>
                      <span>{managementRestaurantId ? `${menuItems.length} loaded` : "New restaurant"}</span>
                    </div>

                    {!managementRestaurantId ? (
                      <p className="detail-empty">Create the restaurant first, then add items to it.</p>
                    ) : (
                      <>
                        <div className="management-form">
                          <label className="management-label">
                            Name
                            <input
                              type="text"
                              value={itemForm.name}
                              onChange={(event) => setItemForm((current) => ({ ...current, name: event.target.value }))}
                            />
                          </label>
                          <label className="management-label">
                            Price
                            <input
                              type="text"
                              value={itemForm.price}
                              onChange={(event) => setItemForm((current) => ({ ...current, price: event.target.value }))}
                            />
                          </label>
                        </div>

                        <div className="management-actions">
                          <button className="inline-action" onClick={handleSaveItem} type="button" disabled={isManagementLoading}>
                            Save item
                          </button>
                        </div>
                      </>
                    )}
                  </div>

                  <div className="detail-section">
                    <div className="detail-section-header">
                      <h4>Current items</h4>
                      <span>{isManagementLoading ? "Loading..." : "Ready"}</span>
                    </div>
                    {managementRestaurantId && menuItems.length ? (
                      <div className="menu-list">
                        {menuItems.map((item) => (
                          <article className="menu-card" key={item.item_id || item.id}>
                            <div>
                              <h5>{item.name}</h5>
                              <p>Item ID: {item.item_id || item.id} · Menu ID: {item.menuId}</p>
                            </div>
                            <div className="menu-actions">
                              <strong>${Number(item.price || 0).toFixed(2)}</strong>
                              <button className="inline-action" onClick={() => populateItemForm(item)} type="button">
                                Edit
                              </button>
                              <button className="inline-action inline-action-muted" onClick={() => handleDeleteItem(item.item_id || item.id)} type="button">
                                Remove
                              </button>
                            </div>
                          </article>
                        ))}
                      </div>
                    ) : (
                      <p className="detail-empty">
                        {managementRestaurantId
                          ? "No items for this restaurant yet."
                          : "Select an eligible restaurant or start creating a new one to access item controls."}
                      </p>
                    )}
                  </div>
                </div>
              ) : null}
            </div>
          </section>
        ) : null}

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
                <div className="cart-header-actions">
                  <button
                    className={isRestaurantFavourite(selectedRestaurant.restaurant_id || selectedRestaurant.id) ? "star-action active" : "star-action"}
                    onClick={() => handleToggleFavouriteRestaurant(selectedRestaurant)}
                    type="button"
                    aria-label={
                      isRestaurantFavourite(selectedRestaurant.restaurant_id || selectedRestaurant.id)
                        ? "Remove restaurant from favourites"
                        : "Add restaurant to favourites"
                    }
                    disabled={pendingFavouriteRestaurantId === String(selectedRestaurant.restaurant_id || selectedRestaurant.id)}
                  >
                    <svg viewBox="0 0 24 24" aria-hidden="true">
                      <path d="M12 2.8l2.84 5.76 6.36.92-4.6 4.48 1.08 6.33L12 17.3l-5.68 2.99 1.08-6.33-4.6-4.48 6.36-.92L12 2.8z" />
                    </svg>
                  </button>
                  <button className="ghost-action" onClick={handleCloseRestaurant} type="button">
                    Close
                  </button>
                </div>
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
                  <button
                    type="button"
                    className="inline-action"
                    onClick={openCheckoutPanel}
                    disabled={!cart?.items?.length}
                  >
                    Checkout
                  </button>
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
                  <div className="management-actions">
                    <button
                      type="button"
                      className="inline-action"
                      onClick={openCheckoutPanel}
                      disabled={!cartDisplayEntries.length}
                    >
                      Checkout
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </section>
        ) : null}

        {showFavourites ? (
          <section className="detail-overlay" onClick={() => setShowFavourites(false)}>
            <div
              className="cart-panel"
              onClick={(event) => event.stopPropagation()}
              role="dialog"
              aria-modal="true"
            >
              <div className="detail-header">
                <div>
                  <p className="eyebrow">Favorites</p>
                  <h3>Your favourite restaurants</h3>
                  <p className="section-copy">
                    Quick access to the restaurants you&apos;ve starred.
                  </p>
                </div>
                <div className="cart-header-actions">
                  <button className="ghost-action" onClick={() => setShowFavourites(false)} type="button">
                    Close
                  </button>
                </div>
              </div>

              {favouritesError ? <div className="detail-state"><p>{favouritesError}</p></div> : null}
              {favouritesNotice ? <div className="detail-state cart-state-success"><p>{favouritesNotice}</p></div> : null}

              <div className="detail-section">
                <div className="detail-section-header">
                  <h4>Saved restaurants</h4>
                  <span>{favouriteRestaurants.length} saved</span>
                </div>
                {isFavouritesLoading ? (
                  <p className="detail-empty">Loading favourites...</p>
                ) : favouriteRestaurants.length ? (
                  <div className="menu-list">
                    {favouriteRestaurants.map((restaurant) => (
                      <article className="menu-card favourite-card" key={restaurant.restaurant_id || restaurant.id}>
                        <div>
                          <h5>{restaurant.name}</h5>
                          <p>{restaurant.cuisine} · {restaurant.restaurantAddress || "Address unavailable"}</p>
                        </div>
                        <div className="menu-actions">
                          <button
                            type="button"
                            className="inline-action"
                            onClick={() => {
                              setShowFavourites(false);
                              handleRestaurantSelect(restaurant);
                            }}
                          >
                            Open
                          </button>
                          <button
                            type="button"
                            className="star-action active"
                            onClick={() => handleToggleFavouriteRestaurant(restaurant)}
                            aria-label="Remove restaurant from favourites"
                            disabled={pendingFavouriteRestaurantId === String(restaurant.restaurant_id || restaurant.id)}
                          >
                            <svg viewBox="0 0 24 24" aria-hidden="true">
                              <path d="M12 2.8l2.84 5.76 6.36.92-4.6 4.48 1.08 6.33L12 17.3l-5.68 2.99 1.08-6.33-4.6-4.48 6.36-.92L12 2.8z" />
                            </svg>
                          </button>
                        </div>
                      </article>
                    ))}
                  </div>
                ) : (
                  <p className="detail-empty">No favourite restaurants yet. Tap the star on a restaurant to save it here.</p>
                )}
              </div>
            </div>
          </section>
        ) : null}

        {showCheckout ? (
          <section className="detail-overlay" onClick={handleCloseCheckout}>
            <div
              className="cart-panel checkout-panel"
              onClick={(event) => event.stopPropagation()}
              role="dialog"
              aria-modal="true"
            >
              <div className="detail-header">
                <div>
                  <p className="eyebrow">Checkout</p>
                  <h3>{checkoutResult ? "Order confirmed" : (cart?.restaurant || "Complete your order")}</h3>
                  <p className="section-copy">
                    Use a saved card or enter a new one. This flow uses the backend checkout and delivery APIs.
                  </p>
                </div>
                <div className="cart-header-actions">
                  <button className="ghost-action" onClick={handleCloseCheckout} type="button">
                    Close
                  </button>
                </div>
              </div>

              {checkoutError ? <div className="detail-state"><p>{checkoutError}</p></div> : null}
              {checkoutNotice ? <div className="detail-state cart-state-success"><p>{checkoutNotice}</p></div> : null}

              {checkoutResult ? (
                <div className="cart-modal-grid">
                  <div className="detail-section">
                    <div className="detail-section-header">
                      <h4>Payment result</h4>
                      <span>{checkoutResult.status}</span>
                    </div>
                    <div className="checkout-summary-grid">
                      <p>Transaction</p>
                      <strong>{checkoutResult.transaction_id || "Unavailable"}</strong>
                      <p>Order ID</p>
                      <strong>{checkoutResult.order_id || "Unavailable"}</strong>
                      <p>Subtotal</p>
                      <strong>${Number(checkoutResult.subtotal || 0).toFixed(2)}</strong>
                      <p>Tax</p>
                      <strong>${Number(checkoutResult.tax || 0).toFixed(2)}</strong>
                      <p>Delivery fee</p>
                      <strong>${Number(checkoutResult.delivery_fee || 0).toFixed(2)}</strong>
                      <p>Final total</p>
                      <strong>${Number(checkoutResult.amount || 0).toFixed(2)}</strong>
                    </div>
                  </div>

                  <div className="detail-section">
                    <div className="detail-section-header">
                      <h4>Delivery</h4>
                      <span>{checkoutOrderSummary?.status_label || "Starting"}</span>
                    </div>
                    {checkoutOrderSummary ? (
                      <div className="checkout-summary-grid">
                        <p>Restaurant</p>
                        <strong>{checkoutOrderSummary.restaurant}</strong>
                        <p>Status</p>
                        <strong>{checkoutOrderSummary.status_label}</strong>
                        <p>ETA</p>
                        <strong>{checkoutOrderSummary.estimated_delivery || "On the way"}</strong>
                        <p>Total</p>
                        <strong>${Number(checkoutOrderSummary.total || 0).toFixed(2)}</strong>
                      </div>
                    ) : (
                      <p className="detail-empty">The order was created, but the delivery summary is still loading.</p>
                    )}
                  </div>
                </div>
              ) : (
                <div className="cart-modal-grid">
                  <div className="detail-section">
                    <div className="detail-section-header">
                      <h4>Payment</h4>
                      <span>{savedPaymentMethods.length} saved</span>
                    </div>

                    <div className="checkout-toggle-row">
                      <button
                        type="button"
                        className={checkoutMethodMode === "saved" ? "chip active" : "chip"}
                        onClick={() => setCheckoutMethodMode("saved")}
                        disabled={!savedPaymentMethods.length}
                      >
                        Saved card
                      </button>
                      <button
                        type="button"
                        className={checkoutMethodMode === "new" ? "chip active" : "chip"}
                        onClick={() => setCheckoutMethodMode("new")}
                      >
                        New card
                      </button>
                    </div>

                    {isCheckoutLoading ? (
                      <p className="detail-empty">Loading payment options...</p>
                    ) : null}

                    {!isCheckoutLoading && checkoutMethodMode === "saved" ? (
                      savedPaymentMethods.length ? (
                        <div className="saved-method-list">
                          {savedPaymentMethods.map((method) => (
                            <label className="saved-method-card" key={method.method_id}>
                              <input
                                type="radio"
                                name="saved-payment-method"
                                value={method.method_id}
                                checked={selectedPaymentMethodId === method.method_id}
                                onChange={(event) => setSelectedPaymentMethodId(event.target.value)}
                              />
                              <div>
                                <strong>
                                  {method.card_holder_name} · {method.card_type}
                                </strong>
                                <p>
                                  Ending in {method.last_four} · {String(method.expiry_month).padStart(2, "0")}/{method.expiry_year}
                                  {method.is_default ? " · Default" : ""}
                                </p>
                              </div>
                            </label>
                          ))}
                        </div>
                      ) : (
                        <p className="detail-empty">No saved cards yet. Switch to new card to enter one.</p>
                      )
                    ) : null}

                    {!isCheckoutLoading && checkoutMethodMode === "new" ? (
                      <div className="management-form">
                        <label className="management-label">
                          Card holder name
                          <input
                            type="text"
                            value={paymentForm.card_holder_name}
                            onChange={(event) => setPaymentForm((current) => ({ ...current, card_holder_name: event.target.value }))}
                          />
                        </label>
                        <label className="management-label">
                          Card number
                          <input
                            type="text"
                            inputMode="numeric"
                            value={paymentForm.card_number}
                            onChange={(event) => setPaymentForm((current) => ({ ...current, card_number: event.target.value }))}
                          />
                        </label>
                        <div className="checkout-inline-grid">
                          <label className="management-label">
                            Expiry month
                            <input
                              type="number"
                              min="1"
                              max="12"
                              value={paymentForm.expiry_month}
                              onChange={(event) => setPaymentForm((current) => ({ ...current, expiry_month: event.target.value }))}
                            />
                          </label>
                          <label className="management-label">
                            Expiry year
                            <input
                              type="number"
                              min="2024"
                              value={paymentForm.expiry_year}
                              onChange={(event) => setPaymentForm((current) => ({ ...current, expiry_year: event.target.value }))}
                            />
                          </label>
                          <label className="management-label">
                            CVV
                            <input
                              type="password"
                              inputMode="numeric"
                              value={paymentForm.cvv}
                              onChange={(event) => setPaymentForm((current) => ({ ...current, cvv: event.target.value }))}
                            />
                          </label>
                        </div>
                        <label className="management-label">
                          Card type
                          <select
                            className="auth-select"
                            value={paymentForm.card_type}
                            onChange={(event) => setPaymentForm((current) => ({ ...current, card_type: event.target.value }))}
                          >
                            <option value="credit">Credit</option>
                            <option value="debit">Debit</option>
                          </select>
                        </label>
                        <label className="checkout-checkbox">
                          <input
                            type="checkbox"
                            checked={savePaymentMethod}
                            onChange={(event) => setSavePaymentMethod(event.target.checked)}
                          />
                          <span>Save this card to my account</span>
                        </label>
                      </div>
                    ) : null}
                  </div>

                  <div className="detail-section">
                    <div className="detail-section-header">
                      <h4>Order summary</h4>
                      <span>{userProfile.address || "No saved address"}</span>
                    </div>
                    <div className="checkout-summary-grid">
                      <p>Restaurant</p>
                      <strong>{cart?.restaurant || selectedRestaurant?.name || "Current cart"}</strong>
                      <p>Subtotal</p>
                      <strong>${Number(cart?.subtotal || 0).toFixed(2)}</strong>
                      <p>Discount</p>
                      <strong>${Number(cart?.totalDiscount || 0).toFixed(2)}</strong>
                      <p>Cart total</p>
                      <strong>${Number(cart?.checkout_total || 0).toFixed(2)}</strong>
                    </div>
                    <p className="management-helper">
                      Delivery fee and tax are calculated by the backend during checkout using your saved account address.
                    </p>
                    <div className="management-actions">
                      <button
                        type="button"
                        className="inline-action"
                        onClick={handleCheckoutSubmit}
                        disabled={isCheckoutLoading || !cart?.items?.length}
                      >
                        {isCheckoutLoading ? "Processing..." : "Place order"}
                      </button>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </section>
        ) : null}
      </main>
    </div>
  );
}

export default App;
