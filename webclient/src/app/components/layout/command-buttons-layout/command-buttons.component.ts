import { Component, OnInit, ElementRef, ViewChild } from '@angular/core';
import { GlobalService } from 'src/app/services/global/global.service';
import { saveAs } from 'file-saver';
import { Router } from '@angular/router';
import { MatDialog } from '@angular/material/dialog';
import { IDomain } from 'src/app/interfaces/common/IDomain';
import { IConfirmationResponse } from 'src/app/interfaces/client/IConfirmationResponse';
import { DeploymentService } from 'src/app/services/deployment/deployment.service';
import { S3Service } from 'src/app/services/s3/s3.service';
import { MessageHandlerService } from 'src/app/services/message-handler/message-handler.service';
import { ProgressHandlerService } from 'src/app/services/progress-handler/progress-handler.service';
import { BrowseStoredFilesComponent } from '../../dialogs/browse-stored-files-dialog/browse-stored-files.component';
import { ProgressSpinnerComponent } from '../../progress-spinner/progress-spinner.component';
import { S3LoginComponent } from '../../dialogs/s3-login-dialog/s3-login.component';
import { FileSelectionDialogComponent } from '../../dialogs/file-selection-dialog/file-selection-dialog.component';
import { DeploymentProgressModalComponent } from '../../dialogs/deplopyment-progress-modal/deployment-progress-modal.component';
import { ConfirmationModalComponent } from '../../dialogs/deployment-confirmation-dialog/confirmation-modal.component';
import { ConfirmDialogComponent } from '../../dialogs/confirm-dialog/confirm-dialog.component';
@Component({
  selector: 'app-command-buttons',
  templateUrl: './command-buttons.component.html',
  styleUrls: ['./command-buttons.component.scss'],
})
export class CommandButtonsComponent implements OnInit {
  @ViewChild('fileInput') fileInput: ElementRef;
  uploader: any;
  form: IDomain[];
  constructor(
    private s3Service: S3Service,
    private deploymentService: DeploymentService,
    private globalService: GlobalService,
    private router: Router,
    private messageHandlerService: MessageHandlerService,
    public dialog: MatDialog,
    private progressHandlerService: ProgressHandlerService
  ) {}

  ngOnInit(): void {}

  home() {
    this.router.navigate(['']);
    this.globalService.resetActiveDomainText();
  }

  deleteAll() {
    const dialogRef = this.dialog.open(ConfirmDialogComponent, {
      data: {
        header: 'Reset All Data?',
        content: 'Are you sure you wish to reset ALL data?',
        confrimButtonText: 'Reset',
      },
    });
    dialogRef.afterClosed().subscribe((result) => {
      if (result) {
        this.globalService.clearAll().then((result) => {
          if (result) {
            this.router.navigate(['']);
          }
        });
      }
    });
  }

  openS3Browser() {
    this.s3Service.listDeploymentFiles().then((fileList) => {
      this.progressHandlerService.onActionCompleted.next(true);
      const dialogRef = this.dialog.open(BrowseStoredFilesComponent, {
        data: fileList,
      });
      dialogRef.afterClosed().subscribe((result: any) => {
        if (result.loaded) {
          this.globalService.uploadForm(JSON.stringify(result.loadedForm));
          this.messageHandlerService.onUserMessage.next('Loaded Successfuly!');
          this.globalService.refreshRequired.next({
            pageChanged: true,
            domainChanged: true,
          });
          this.router.navigate(['']);
        }
      });
    });
  }

  browse() {
    this.dialog.open(ProgressSpinnerComponent, {
      data: {
        header: 'Loading Files From S3 Bucket',
        subheader: 'Searching for files on S3 bucket...',
      },
      disableClose: true,
    });
    this.s3Service.isCredentialsLoaded().then((valid) => {
      if (valid) {
        this.openS3Browser();
      } else {
        const dialogRef = this.dialog.open(S3LoginComponent, {
          disableClose: true,
        });
        dialogRef.afterClosed().subscribe((valid: any) => {
          if (valid.response) {
            this.openS3Browser();
          } else {
            this.progressHandlerService.onActionCompleted.next(true);
          }
        });
      }
    });
  }

  upload() {
    this.fileInput.nativeElement.click();
  }

  private openProgressDialog(domainsToInstall: IDomain[], deleteMode: boolean) {
    const dialogRef = this.dialog.open(DeploymentProgressModalComponent, {
      data: { domains: domainsToInstall, deleteMode: deleteMode },
      disableClose: true,
    });
    const deploymentService = this.deploymentService;
    dialogRef.afterClosed().subscribe((result: any) => {
      console.log(result);
      deploymentService.closeSocket();
    });
  }

  async export(domainsToExport?: IDomain[], s3: boolean = true) {
    return await this.globalService.export(domainsToExport, s3);
  }

  public async openConfirmationDialog(deleteMode: boolean) {
    const notCompleted = this.globalService.verifyMandatory();
    const modifiedDomainList = await this.globalService.getModifiedList();
    if (notCompleted.length === 0 && modifiedDomainList.length > 0) {
      if (!deleteMode) {
        // await this.storeToS3();
        await this.globalService.export();
      }
      const dialogRef = this.dialog.open(ConfirmationModalComponent, {
        data: {
          modifiedDomainList: modifiedDomainList,
          deleteMode: deleteMode,
        },
        disableClose: true,
      });
      dialogRef
        .afterClosed()
        .subscribe(async (result: IConfirmationResponse) => {
          if (result && result.response && result.domainList.length > 0) {
            /* if (!deleteMode) {
              await this.export();
            } */
            this.openProgressDialog(result.domainList, deleteMode);
          }
        });
    } else {
      if (modifiedDomainList.length === 0) {
        this.messageHandlerService.onErrorOccured.next(`No pages with data`);
      } else {
        let incompleteStr =
          'Please complete the following mandatory components: \n';
        notCompleted.forEach((domain) => {
          incompleteStr += domain.displayName + ' ,';
        });
        this.messageHandlerService.onErrorOccured.next(
          `${incompleteStr.substring(0, incompleteStr.length - 1)}`
        );
      }
    }
  }

  onFileChanged(event) {
    const selectedFile = event.target.files[0];
    const fileReader = new FileReader();
    fileReader.readAsText(selectedFile, 'UTF-8');
    fileReader.onload = () => {
      const result = this.globalService.uploadForm(
        fileReader.result.toString()
      );
      if (!result) {
        return;
      }
      this.fileInput.nativeElement.value = '';
      this.globalService.refreshRequired.next({
        pageChanged: true,
        domainChanged: true,
      });
      this.router.navigate(['']);
    };
    fileReader.onerror = () => {
      this.messageHandlerService.onErrorOccured.next('Failed to read file');
      this.router.navigate(['']);
    };
  }
}
