export interface IUser {
  userToken: string;
  userTokenRefresh: string;
  userProfile: IUserProfile | null;
  getLocalUserList: Array<any> | null;
}

export enum ERealmAccessRole {
  OFFLINE_ACCESS = "offline_access",
  UMA_AUTHORIZATION = "uma_authorization"
}

export enum EResourceAccessRole {
  MANAGE_ACCOUNT = "manage-account",
  MANAGE_ACCOUNT_LINKS = "manage-account-links",
  VIEW_PROFILE = "view-profile"
}

export interface IUserProfile {
  exp: number;
  iat: number;
  auth_time: number;
  jti: string;
  iss: string;
  aud: string;
  sub: string;
  typ: string;
  azp: string;
  nonce: string;
  session_state: string;
  acr: string;
  "allowed-origins": Array<string>;
  realm_access: { roles: Array<ERealmAccessRole> };
  resource_access: {
    account: {
      roles: Array<EResourceAccessRole>;
    };
  };
  scope: string;
  email_verified: boolean;
  "first login": boolean;
  preferred_username: string;
  email: string;
  firstName: string;
  lastName: string;
}
