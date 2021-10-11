import path from "path";
import { CompletedMessage } from "../messages/completed-message";
import { ErrordMessage } from "../messages/error-message";
import { IGlobalVariable } from "../interfaces/server/IGlobalVariable";
import { IDeploymentPage } from "../interfaces/server/IDeploymentPage";
import { IDomain } from "../interfaces/common/IDomain";
import { IPage } from "../interfaces/common/IPage";
import { Logger } from "../logger/logger";
import app from "../app";
import { IExecuter } from "../interfaces/server/IExecuter";
import { DeploymentExecutionMaster } from "./deployment-execution-master";
import { LogLine } from "./logline-message";
export class DeploymentExecuter {
  private globalVariables: IGlobalVariable[] = [];
  private output_folder: string;
  timeStamp = 0;
  constructor(public domains: IDomain[], public deploymentIdentifier: string) {
    this.timeStamp = new Date().getMilliseconds();
    this.output_folder = `outputs-${deploymentIdentifier}`;
  }

  public static getWorkingFolder(identifier: string): string {
    let workingFolderSuffix = identifier.split(".").pop() || "";
    if (workingFolderSuffix[0] == "0") {
      workingFolderSuffix = workingFolderSuffix.substring(1);
    }
    let workingFolder = path.resolve(
      __dirname,
      `../../../../`,
      `working_folder_${workingFolderSuffix.substring(
        0,
        workingFolderSuffix.length - 1
      )}`
    );
    return workingFolder;
  }

  public static getOutputsFolder(identifier: string): string {
    const workingFolder = DeploymentExecuter.getWorkingFolder(identifier);
    const outputsFoldet = path.join(workingFolder, `outputs-${identifier}`);
    Logger.info("Using outputs folder: " + outputsFoldet);
    return outputsFoldet;
  }

  public async startDeletion(workingFolders: string[]) {
    const deployPages = this.flattenDomains(
      "Deleting",
      "delete",
      workingFolders
    );
    return await this.startExecution(deployPages);
  }

  public static async compressFolder(sourceFolder: string): Promise<any> {
    const fs = require("fs");
    Logger.info(`Compressing: ${sourceFolder}`);
    fs.readdirSync(sourceFolder).forEach((file: any) => {
      Logger.info(file);
    });
    let output = path.join(sourceFolder, "..", "outputs.zip");
    Logger.info(`Destination: ${output}`);
    const archiver = require("archiver");
    const archive = archiver("zip", { zlib: { level: 9 } });
    const stream = fs.createWriteStream(output);
    return new Promise((resolve, reject) => {
      archive
        .directory(sourceFolder, false)
        .on("error", (err: any) => reject(err))
        .pipe(stream);

      stream.on("close", () => resolve(output));
      archive.finalize();
    });
  }

  public async startDeployment(workingFolders: string[]) {
    const deployPages = this.flattenDomains(
      "Starting Deployment",
      "create",
      workingFolders
    );
    return await this.startExecution(deployPages);
  }

  private flattenDomains(
    deployMessage: string,
    verb: string,
    workingFolders: string[]
  ): IDeploymentPage[] {
    const deployPages: IDeploymentPage[] = [];
    let currentPageCounting = 0;
    for (let domain of this.domains) {
      for (let page of domain.pages) {
        for (let input of page.inputs) {
          if (!input.value) {
            if (input.defaultValue != null) {
              input.value = input.defaultValue;
            }
          }
        }
        let createMode = true;
        if (verb != "create") {
          createMode = false;
        }
        const deploymentPage = {
          page,
          executionData: {
            createMode: createMode,
            workingFolder: workingFolders[currentPageCounting],
            parentDomain: domain,
            progress: {
              currentPage: currentPageCounting + 1,
              totalDomains: this.domains.length,
            },
            verb: verb,
            logs: [new LogLine(deployMessage)],
            deploymentIdentifier: this.deploymentIdentifier,
          },
        };
        deployPages.push(deploymentPage);
        currentPageCounting++;
        this.globalVariables.push({
          variableName: "FENNEC_OUTPUTS_FOLDER",
          variableValue: this.output_folder,
        });
        for (let input of page.inputs) {
          if (input.global) {
            this.globalVariables.push({
              variableName: input.serverValue,
              variableValue: input.value,
            });
          }
        }
      }
    }
    return deployPages;
  }

  public async createWorkingFolders() {
    const workingFolders: string[] = [];
    for (
      let domainIndex = 0;
      domainIndex < this.domains.length;
      domainIndex++
    ) {
      for (
        let pageIndex = 0;
        pageIndex < this.domains[domainIndex].pages.length;
        pageIndex++
      ) {
        const page = this.domains[domainIndex].pages[pageIndex];
        workingFolders.push(await this.backupWorkingFolder(page));
      }
    }
    Logger.info(`Workingfolder: ${workingFolders}`);
    await this.copyCommonFolder();
    return workingFolders;
  }

  private async startExecution(deployPages: IDeploymentPage[]) {
    for (let deployPage of deployPages) {
      if (
        DeploymentExecutionMaster.killedDeployments.indexOf(
          this.deploymentIdentifier
        ) == -1
      ) {
        try {
          deployPage.executionData.progress.totalPages = deployPages.length;
          if (
            deployPages.length > 1 &&
            deployPage.page.name == "cluster" &&
            !deployPage.executionData.createMode
          ) {
            this.sendFinalMessage(0, deployPage);
            continue;
          }
          deployPage.executionData.progress.totalPages = deployPages.length;
          const exitCode = await this.executeScript(deployPage);
          this.sendFinalMessage(exitCode, deployPage);
        } catch (error) {
          Logger.error(error.message, error.stack);
          const deploymentMessage = new ErrordMessage(deployPage, error);
          app.socketServer.sendMessage(
            this.deploymentIdentifier,
            deploymentMessage
          );
          return;
        }
      } else {
        Logger.info(`Killed all (${this.deploymentIdentifier})`);
        const index = DeploymentExecutionMaster.killedDeployments.indexOf(
          this.deploymentIdentifier,
          0
        );
        if (index > -1) {
          DeploymentExecutionMaster.killedDeployments.splice(index, 1);
        }
        return;
      }
    }
  }

  private sendFinalMessage(exitCode: any, deployPage: IDeploymentPage) {
    let deploymentMessage;
    deployPage.executionData.final = true;
    if (exitCode === 0) {
      deploymentMessage = new CompletedMessage(deployPage);
    } else {
      deploymentMessage = new ErrordMessage(deployPage);
    }
    app.socketServer.sendMessage(this.deploymentIdentifier, deploymentMessage);
  }

  private getDeployemntExecuter(deploymentPage: IDeploymentPage): IExecuter {
    switch (deploymentPage.page.executer) {
      case "pwsh": {
        return {
          executer: deploymentPage.page.executer,
          file: `${deploymentPage.executionData.verb}.ps1`,
        };
      }
      case "python": {
        return {
          executer: "python3",
          addional_args: "-u",
          file: `${deploymentPage.executionData.verb}.py`,
        };
      }
      default: {
        return {
          executer: "bash",
          file: `${deploymentPage.executionData.verb}.sh`,
        };
      }
    }
  }

  private async copyFolder(
    source: string[],
    target: string[]
  ): Promise<{ source: string; target: string }> {
    const fs = require("fs-extra");
    const path = require("path");
    const shell = require("shelljs");
    const targetFolder = path.join.apply(null, target);
    const sourceFolder = path.join.apply(null, source);
    shell.mkdir("-p", targetFolder);
    await fs.copy(sourceFolder, targetFolder);
    return { source: sourceFolder, target: targetFolder };
  }

  private async copyCommonFolder() {
    await this.copyFolder(
      [path.resolve(process.env.COMPONENTS_ROOT!), "fennec"],
      [`${path.resolve(process.env.WORKING_ROOT!)}_${this.timeStamp}`, `fennec`]
    );
  }

  private async backupWorkingFolder(page: IPage): Promise<string> {
    try {
      const result = await this.copyFolder(
        [
          path.resolve(process.env.COMPONENTS_ROOT!),
          this.removedCloned(page.name),
        ],
        [
          `${path.resolve(process.env.WORKING_ROOT!)}_${this.timeStamp}`,
          `${page.name}`,
        ]
      );
      return result.target;
    } catch (err) {
      Logger.error(err.message, err.stack);
      throw new Error(err.message);
    }
  }

  private removedCloned(pageName: string): string {
    if (pageName.indexOf("_fenneccloned") > -1) {
      const cleanedPageName = pageName.substring(0, pageName.lastIndexOf("_"));
      return cleanedPageName;
    }
    return pageName;
  }

  private async executeScript(pageToExecute: IDeploymentPage) {
    try {
      const executer = this.getDeployemntExecuter(pageToExecute);
      const deploymentExecutionMaster = new DeploymentExecutionMaster(
        this.globalVariables
      );
      const deploymentProcess = await deploymentExecutionMaster.startListening(
        pageToExecute,
        executer
      );
      await new Promise((resolve, reject) => {
        deploymentProcess.on("close", resolve);
      }).catch((error) => {
        Logger.error(error.message, error.stack);
      });
      return deploymentExecutionMaster.exitCode;
    } catch (error) {
      Logger.error(error.message, error.stack);
    }
  }
}
