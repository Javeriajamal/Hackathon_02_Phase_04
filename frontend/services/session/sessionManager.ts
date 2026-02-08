// Session management utilities for authentication

class SessionManager {
  private static readonly TOKEN_KEY = 'token';
  private static readonly USER_KEY = 'user';

  /**
   * Store the authentication token
   */
  static setToken(token: string): void {
    localStorage.setItem(this.TOKEN_KEY, token);
  }

  /**
   * Get the stored authentication token
   */
  static getToken(): string | null {
    return localStorage.getItem(this.TOKEN_KEY);
  }

  /**
   * Remove the authentication token
   */
  static removeToken(): void {
    localStorage.removeItem(this.TOKEN_KEY);
  }

  /**
   * Store user information
   */
  static setUser(user: any): void {
    localStorage.setItem(this.USER_KEY, JSON.stringify(user));
  }

  /**
   * Get stored user information
   */
  static getUser(): any {
    const userStr = localStorage.getItem(this.USER_KEY);
    return userStr ? JSON.parse(userStr) : null;
  }

  /**
   * Remove stored user information
   */
  static removeUser(): void {
    localStorage.removeItem(this.USER_KEY);
  }

  /**
   * Check if user is authenticated
   */
  static isAuthenticated(): boolean {
    const token = this.getToken();
    return token !== null && token !== undefined;
  }

  /**
   * Clear all session data
   */
  static clearSession(): void {
    this.removeToken();
    this.removeUser();
  }

  /**
   * Get token expiration information (if available in token)
   */
  static getTokenExpiration(): number | null {
    const token = this.getToken();
    if (!token) return null;

    try {
      // Decode JWT token to get expiration
      const payload = token.split('.')[1];
      const decodedPayload = atob(payload);
      const parsedPayload = JSON.parse(decodedPayload);

      if (parsedPayload.exp) {
        return parsedPayload.exp * 1000; // Convert to milliseconds
      }
    } catch (error) {
      console.error('Error decoding token:', error);
    }

    return null;
  }

  /**
   * Check if token is expired
   */
  static isTokenExpired(): boolean {
    const expiration = this.getTokenExpiration();
    if (!expiration) return true;

    return Date.now() > expiration;
  }

  /**
   * Check if session is valid (token exists and is not expired)
   */
  static isSessionValid(): boolean {
    if (!this.isAuthenticated()) return false;
    return !this.isTokenExpired();
  }
}

export default SessionManager;