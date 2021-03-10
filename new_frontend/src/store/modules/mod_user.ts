import { Module, Mutation, VuexModule } from "vuex-module-decorators";
import { IUserProfile } from "@/types";
import { parseJWT, setCookie } from "@/core/utility";

@Module({
  name: "mod_user",
  namespaced: true,
})
export default class UserModule extends VuexModule {
  public userToken: string | null = null;
  public userTokenRefresh: string | null = null;

  // Mutations
  @Mutation
  setToken(accessToken: string, refreshToken: string) {
    setCookie("loggedInUser", accessToken, 1 /* 1 day */);

    localStorage.setItem("currentUser", accessToken);
    localStorage.setItem("vue-token", accessToken);
    localStorage.setItem("vue-refresh-token", refreshToken);

    this.userToken = accessToken;
    this.userTokenRefresh = refreshToken;
  }

  // Actions

  // Getters
  public get userTokenInfo(): IUserProfile | null {
    return !this.userToken ? null : parseJWT(this.userToken);
  }
  public get isUserLoggedIn() {
    return !!this.userToken;
  }

  public get isUserFirstLoggedIn() {
    return;
  }
}
