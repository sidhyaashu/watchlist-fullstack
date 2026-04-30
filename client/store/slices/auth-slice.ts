import { createSlice, PayloadAction } from "@reduxjs/toolkit";
import { AuthState, ProfileResponse } from "../../types/api";

const initialState: AuthState = {
  user: null,
  access_token: null,
  isAuthenticated: false,
  isLoading: true,
  error: null,
};

const authSlice = createSlice({
  name: "auth",
  initialState,
  reducers: {
    setCredentials: (
      state,
      action: PayloadAction<{ user: ProfileResponse | null; access_token: string }>
    ) => {
      const { user, access_token } = action.payload;
      state.user = user;
      state.access_token = access_token;
      state.isAuthenticated = true;
      state.isLoading = false;
      state.error = null;
    },
    updateUser: (state, action: PayloadAction<ProfileResponse>) => {
      state.user = action.payload;
      state.isAuthenticated = true;
      state.isLoading = false;
    },
    updateTokens: (state, action: PayloadAction<{ access_token: string }>) => {
      state.access_token = action.payload.access_token;
    },
    logout: (state) => {
      state.user = null;
      state.access_token = null;
      state.isAuthenticated = false;
      state.isLoading = false;
    },
    setLoading: (state, action: PayloadAction<boolean>) => {
      state.isLoading = action.payload;
    },
    setError: (state, action: PayloadAction<string | null>) => {
      state.error = action.payload;
      state.isLoading = false;
    },
  },
});

export const { setCredentials, updateUser, updateTokens, logout, setLoading, setError } = authSlice.actions;
export default authSlice.reducer;
