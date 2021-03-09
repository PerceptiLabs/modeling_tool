import { Module, Mutation, VuexModule } from "vuex-module-decorators";

@Module({
  name: "mod_template",
  namespaced: true
})
export default class TemplateModule extends VuexModule {
  private _someData = 0;

  @Mutation
  public increment() {
    this._someData++;
  }

  @Mutation
  public decrement() {
    this._someData--;
  }

  @Mutation
  public reset() {
    this._someData = 0;
  }

  get getData() {
    return this._someData;
  }
}
