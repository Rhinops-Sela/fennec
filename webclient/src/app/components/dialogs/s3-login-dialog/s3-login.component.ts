import { Component, OnInit } from '@angular/core';
import { MatDialogRef, MatDialog } from '@angular/material/dialog';
import { IS3Bucket } from 'src/app/interfaces/client/IS3';
import { FormBuilder } from '@angular/forms';
import { MessageHandlerService } from 'src/app/services/message-handler/message-handler.service';
import { ProgressHandlerService } from 'src/app/services/progress-handler/progress-handler.service';
import { S3Service } from 'src/app/services/s3/s3.service';
import { ProgressSpinnerComponent } from '../../progress-spinner/progress-spinner.component';

@Component({
  selector: 'app-s3-login',
  templateUrl: './s3-login.component.html',
  styleUrls: ['./s3-login.component.scss'],
})
export class S3LoginComponent implements OnInit {
  credentialsValid: boolean;
  credentialsForm;
  cancel = false;
  constructor(
    private s3Service: S3Service,
    public dialogRef: MatDialogRef<S3LoginComponent>,
    private formBuilder: FormBuilder,
    private errorHandler: MessageHandlerService,
    public dialog: MatDialog,
    private progressHandlerService: ProgressHandlerService
  ) {}

  ngOnInit(): void {
    this.credentialsForm = this.formBuilder.group({
      accessKeyId: '',
      secretAccessKey: '',
      region: '',
      bucketName: '',
      storeCredentials: false,
    });
  }

  public verifyCredentials() {
    if (!this.credentialsForm.valid || this.cancel) {
      return;
    }
    const bucketInfo: IS3Bucket = {
      accessKeyId: this.credentialsForm.controls.accessKeyId.value,
      secretAccessKey: this.credentialsForm.controls.secretAccessKey.value,
      region: this.credentialsForm.controls.region.value,
      bucketName: this.credentialsForm.controls.bucketName.value,
      storeCredentials: this.credentialsForm.controls.storeCredentials.value,
    };
    this.dialog.open(ProgressSpinnerComponent, {
      data: {
        header: 'Verifing S3 Credentials',
        subheader: 'Checking S3 Connection Status...',
      },
      disableClose: true,
    });
    this.s3Service.setCredentials(bucketInfo).then((response) => {
      if (!response) {
        this.errorHandler.onErrorOccured.next('Invalid S3 Credentials');
      }
      this.dialogRef.close({ response: response });
    });
    this.progressHandlerService.onActionCompleted.next(true);
  }

  public onCancel() {
    this.cancel = true;
    this.dialogRef.close({ response: false });
  }
}
