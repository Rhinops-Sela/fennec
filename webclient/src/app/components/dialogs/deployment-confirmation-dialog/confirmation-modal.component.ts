import { Component, OnInit, Inject } from '@angular/core';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { IDomain } from 'src/app/interfaces/common/IDomain';
import { GlobalService } from 'src/app/services/global/global.service';
@Component({
  selector: 'app-confirmation-modal',
  templateUrl: './confirmation-modal.component.html',
  styleUrls: ['./confirmation-modal.component.scss'],
})
export class ConfirmationModalComponent implements OnInit {
  panelOpenState = true;
  buttonLabel = 'Confirm';
  header = 'Review & Confirm Deployment';
  domainList: IDomain[];
  constructor(
    public globalService: GlobalService,
    public dialogRef: MatDialogRef<ConfirmationModalComponent>,
    @Inject(MAT_DIALOG_DATA) public data: any
  ) {
    this.domainList = this.data.modifiedDomainList;
    if (this.data.deleteMode) {
      this.buttonLabel = 'Delete';
      this.header = 'Review & Confirm Before Deleting';
    }
  }

  ngOnInit(): void {}

  complete(confirm: boolean) {
    this.dialogRef.close({ response: confirm, domainList: this.domainList });
  }
}
