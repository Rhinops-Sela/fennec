import {
  Component,
  OnInit,
  Inject,
  OnDestroy,
  ElementRef,
  ViewChild,
  AfterViewInit,
  ViewChildren,
  QueryList,
} from '@angular/core';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { DeploymentService } from 'src/app/services/deployment/deployment.service';
import { BackendService } from 'src/app/services/backend/backend.service';
import { IDeploymentInfo } from 'src/app/interfaces/client/IDeploymentInfo';
import { IDeploymentMessage } from 'src/app/interfaces/common/IDeploymentMessage';
import { IPage } from 'src/app/interfaces/common/IPage';
import { MessageHandlerService } from 'src/app/services/message-handler/message-handler.service';

@Component({
  selector: 'app-deployment-progress',
  templateUrl: './deployment-progress-modal.component.html',
  styleUrls: ['./deployment-progress-modal.component.scss'],
})
export class DeploymentProgressModalComponent implements OnInit, AfterViewInit {
  @ViewChild('scrollfcontainer', { static: false }) scrollFrame: ElementRef;
  @ViewChildren('item') itemElements: QueryList<any>;
  private scrollContainer: any;
  deploymentCompleted = false;
  cancelPressed = false;
  deploymentStarted = false;
  pagesToInstall: IPage[];
  activePage: IPage;
  displayPage: IPage;
  bufferValue = 0;
  constructor(
    private deploymentService: DeploymentService,
    public dialogRef: MatDialogRef<DeploymentProgressModalComponent>,
    private backendService: BackendService,
    private errorHandler: MessageHandlerService,
    @Inject(MAT_DIALOG_DATA) public data: IDeploymentInfo
  ) {}

  ngOnInit(): void {
    try {
      if (this.data.deleteMode) {
        this.data.domains = this.data.domains.reverse();
      }
      this.pagesToInstall = [];
      if (this.data) {
        for (const domain of this.data.domains) {
          for (const page of domain.pages) {
            this.pagesToInstall.push(page);
          }
        }
        this.activePage = this.pagesToInstall[0];
        this.displayPage = this.activePage;
        this.activePage.logs = [];
      }
    } catch (error) {
      this.errorHandler.onErrorOccured.next(error.message);
      this.close();
    }
  }

  ngAfterViewInit() {
    this.scrollContainer = this.scrollFrame.nativeElement;
    this.itemElements.changes.subscribe((_) => this.onItemElementsChanged());
  }

  private onItemElementsChanged(): void {
    this.scrollContainer.scroll({
      top: this.scrollContainer.scrollHeight,
      left: 0,
      behavior: 'smooth',
    });
  }

  cancelDeployment() {
    this.deploymentService.sendKillMessage();
    this.cancelPressed = true;
  }
  initDeployment() {
    this.backendService
      .startDeployment(this.data.domains, this.data.deleteMode)
      .then((deploymentIdentifier) => {
        this.setupScoket(deploymentIdentifier);
        this.deploymentStarted = true;
        this.deploymentCompleted = false;
        this.cancelPressed = false;
      })
      .catch((error) => {
        this.errorHandler.onErrorOccured.next(
          `${error.response.status} - ${error.response.statusText}`
        );
        this.close();
      });
  }

  private setupScoket(deploymentIdentifier: string) {
    this.deploymentService.setupSocketConnection(deploymentIdentifier);
    this.deploymentService.progressUpdate.subscribe(
      (message: IDeploymentMessage) => {
        this.onDeploymentMessage(message);
      }
    );
  }

  public changeDisplayDomain(pageName: string) {
    if (this.displayPage.name !== pageName) {
      this.displayPage = this.pagesToInstall.find(
        (page) => page.name === pageName
      );
    }
  }

  getPageDisplayName(page: IPage) {
    if (page.repeatable && page.inputs[0].value) {
      return `${page.displayName}-${page.inputs[0].value}`;
    }
    return page.displayName;
  }

  private async onDeploymentMessage(deploymentMessage: IDeploymentMessage) {
    // this.log = deploymentMessage.log;
    if (this.activePage.name !== deploymentMessage.pageName) {
      this.activePage = this.pagesToInstall.find(
        (page) => page.name === deploymentMessage.pageName
      );
      this.displayPage = this.activePage;
      if (deploymentMessage.pageName) {
        this.activePage.name = deploymentMessage.pageName;
      }
      if (!this.activePage.logs) {
        this.activePage.logs = [];
      }
    }

    if (deploymentMessage.error) {
      this.activePage.deploymentIcon = 'clear';
    } else if (
      this.activePage.deploymentIcon !== 'clear' &&
      deploymentMessage.final
    ) {
      this.activePage.deploymentIcon = 'done';
    }
    this.activePage.logs = deploymentMessage.logs;
    // this.displayPage.logs = deploymentMessage.logs;

    if (deploymentMessage.progress) {
      let newBufferValue = Math.round(
        ((deploymentMessage.progress.currentPage-1) /
          deploymentMessage.progress.totalPages) *
          100
      );
      this.bufferValue = newBufferValue;
    } else {
      console.log('missing progress info');
    }
    if (this.deploymentCompleted == false && deploymentMessage.final && deploymentMessage.progress.currentPage == deploymentMessage.progress.totalPages) {
      this.bufferValue = 100;
      this.backendService.downloadOutputsFolder(
        this.deploymentService.deploymentIdentifier
      );
      this.deploymentCompleted = true;
    }
  }

  public close() {
    this.dialogRef.close();
  }
}
