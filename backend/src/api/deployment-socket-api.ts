import { createServer, Server } from "http";
import socketIo from "socket.io";
import { DeploymentEvent } from "../enums/deployment";
import { IDeploymentMessage } from "../interfaces/common/IDeploymentMessage";
import { Logger } from "../logger/logger";
import { DeploymentExecutionMaster } from "../deployment/deployment-execution-master";

export class DeploymentServer {
  private server: Server;
  private io: SocketIO.Server;
  private port: string | number;
  private socket: any;
  constructor(express: any) {
    this.port = process.env.SOCKET_PORT || 9090;
    this.server = createServer(function(req,res){
      // Set CORS headers
      res.setHeader('Access-Control-Allow-Origin', '*');
      res.setHeader('Access-Control-Request-Method', '*');
      res.setHeader('Access-Control-Allow-Methods', 'OPTIONS, GET');
      res.setHeader('Access-Control-Allow-Headers', '*');
      if ( req.method === 'OPTIONS' ) {
        res.writeHead(200);
        res.end();
        return;
      }
    })
    this.io = require("socket.io")(this.server, {
      cors: {
        origin: "*",
        methods: ["GET", "POST"]
      }
    });
    this.listen();
  }

  private listen(): void {
    this.server.listen(this.port, () => {
      Logger.info(`Running server on port ${this.port}`);
    });
    this.io.of('/stream').on(DeploymentEvent.CONNECT, (socket: any) => {
      Logger.info(`Connected client on port: ${this.port}`);
      this.socket = socket;
      socket.on(DeploymentEvent.KILL, (deploymentIdetifier: string) => {
        DeploymentExecutionMaster.killProcess(deploymentIdetifier);
        Logger.info(`Kill Process Requested: ${deploymentIdetifier}`);
      });
      socket.on(DeploymentEvent.DISCONNECT, () => {
        Logger.info("Client disconnected");
      });
    });
  }
  static async delay(ms: number) {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }

  public sendMessage(
    deploymentIdentifier: string,
    deploymentMessage: IDeploymentMessage
  ) {
    if (this.socket) {
      this.socket.emit(deploymentIdentifier, deploymentMessage);
    }
    Logger.info(`${deploymentIdentifier}`, [deploymentMessage]);
  }
}
