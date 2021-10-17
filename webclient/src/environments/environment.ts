
import { FennecConfig } from "../app/interfaces/common/IFennecConfig";
export let environment: FennecConfig;

export function setEnvironnement(env: FennecConfig) {
  environment = env;
  console.log(environment)
}

