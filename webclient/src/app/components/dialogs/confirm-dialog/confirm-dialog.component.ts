import { Component, Inject } from '@angular/core';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { IDialogConfirmationData } from 'src/app/interfaces/client/IConfirmationDialogData';

@Component({
  selector: 'app-confirm-dialog',
  templateUrl: './confirm-dialog.component.html',
  styleUrls: ['./confirm-dialog.component.scss'],
})
export class ConfirmDialogComponent {
  cancelText: string;
  confrimText: string;
  constructor(
    public dialogRef: MatDialogRef<ConfirmDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: IDialogConfirmationData
  ) {
    this.confrimText = data.confrimButtonText || 'Yes';
    this.cancelText = data.cancelButtonText || 'No';
  }

  close(confirm: boolean) {
    this.dialogRef.close(confirm);
  }
}
