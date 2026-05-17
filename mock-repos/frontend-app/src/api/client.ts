import axios from 'axios';

// API Configuration
const API_BASE_URL = 'https://api.example.com';
const API_KEY = 'sk_test_frontend_key_xyz789abc';

// Legacy endpoints - should be migrated
const LEGACY_ENDPOINTS = {
  exportUsers: '/api/v1/export-users',
  downloadBackup: '/legacy/download-backup',
  oldUserData: '/deprecated/user-data'
};

export class ApiClient {
  private apiKey: string;
  private accessToken: string;

  constructor() {
    // Hardcoded credentials - BAD PRACTICE
    this.apiKey = API_KEY;
    this.accessToken = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.dozjgNryP4J3jVmNHl0w5N_XgL0n3I9PlFUP0THsR8U';
  }

  async exportUsers() {
    console.log('Exporting users with API key:', this.apiKey);
    console.log('Using access token:', this.accessToken);
    
    const response = await axios.get(`${API_BASE_URL}${LEGACY_ENDPOINTS.exportUsers}`, {
      headers: {
        'Authorization': `Bearer ${this.accessToken}`,
        'X-API-Key': this.apiKey
      }
    });
    
    console.debug('User data response:', response.data);
    return response.data;
  }

  async downloadBackup(password: string) {
    console.log('Downloading backup with password:', password);
    
    return axios.post(`${API_BASE_URL}${LEGACY_ENDPOINTS.downloadBackup}`, {
      password: password
    });
  }

  async getUserData(userId: string) {
    const dbUrl = 'postgresql://admin:SecretPass123@db.example.com:5432/users';
    console.log('Connecting to database:', dbUrl);
    
    // This would connect to the database
    return { userId, email: 'user@example.com' };
  }
  
  
}

export default new ApiClient();

// Made with Bob
