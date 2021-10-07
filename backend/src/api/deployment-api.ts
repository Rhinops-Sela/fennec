import { Request, Response, request } from "express";
import path from "path";
import { Logger } from "../logger/logger";
import { DeploymentExecuter } from "../deployment/deployment-worker";
import { FormParser } from "../deployment/from-parser";
export let validateJson = async (req: Request, res: Response, next: any) => {
  try {
    return res.status(200).json({ status: true });
  } catch (error) {
    next(error);
  }
};

export let downloadOutputs = async (req: Request, res: Response, next: any) => {
  try {
    const identifier = req.query.identifier?.toString() || "";
    const folder = DeploymentExecuter.getWorkingFolder(identifier);
    let fileName = await DeploymentExecuter.compressFolder(DeploymentExecuter.getOutputsFolder(identifier));
    res.download(path.resolve(fileName));
  } catch (error) {
    Logger.error(error.message, error.stack);
    return res.status(500).json({ error: error.message });
  }
};

export let cleanOutputs = async (req: Request, res: Response, next: any) => {
  try {
    let workingFolder = DeploymentExecuter.getWorkingFolder(
      req.body.identifier
    );
    var rimraf = require("rimraf");
    Logger.info(`Deleting folder: ${workingFolder}`);
    rimraf.sync(workingFolder);
  } catch (error) {
    Logger.error(error.message, error.stack);
    return res.status(500).json({ error: error.message });
  }
};

export let startDeployment = async (req: Request, res: Response, next: any) => {
  try {
    const deleteMode = req.body.deleteMode || false;
    const deploymentIdentifier = `deploymentUpdate-${new Date().toISOString()}`;
    const deploymentExecuter = new DeploymentExecuter(
      req.body.form,
      deploymentIdentifier
    );
    const workingFolders = await deploymentExecuter.createWorkingFolders();
    if (req.query.wait) {
      if (deleteMode) {
        await deploymentExecuter.startDeletion(workingFolders);
      } else {
        await deploymentExecuter.startDeployment(workingFolders);
      }
    } else {
      if (deleteMode) {
        deploymentExecuter.startDeletion(workingFolders);
      } else {
        deploymentExecuter.startDeployment(workingFolders);
      }
    }

    return res.status(200).json(deploymentIdentifier);
  } catch (error) {
    Logger.error(error.message, error.stack);
    return res.status(500).json({ error: error.message });
  }
};

export let getForm = async (req: Request, res: Response, next: any) => {
  try {
    Logger.info("Loading Form: Started");
    const form = await FormParser.getForm();
    Logger.info("Loading Form: Completed");
    return res.status(200).json({ form });
  } catch (error) {
    Logger.error("Failed To Read JSON file", error.stack);
    next(error);
  }
};
