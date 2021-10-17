import { Injectable } from '@angular/core';
import io from 'socket.io-client';
import { Subject } from 'rxjs';
import { environment } from "src/environments/environment";
@Injectable({
  providedIn: 'root',
})
export class DeploymentService {
  public progressUpdate: Subject<any> = new Subject<any>();
  deploymentIdentifier: string;
  socketUrl:string;
  socket: SocketIOClient.Socket;
  constructor() {
    this.socketUrl = environment.socketUrl;
  }

  setupSocketConnection(deploymentIdentifier: string) {
    this.deploymentIdentifier = deploymentIdentifier;
    this.socket = io(this.socketUrl);
    this.socket.on(this.deploymentIdentifier, (data: string) => {
      this.progressUpdate.next(data);
    });
  }

  sendKillMessage() {
    this.socket.emit('kill', this.deploymentIdentifier);
  }

  

  closeSocket() {
    if (!this.socket) {
      return;
    }
    this.socket = this.socket.close();
  }
}
function saveAs(blob: Blob, arg1: string) {
  throw new Error('Function not implemented.');
}

