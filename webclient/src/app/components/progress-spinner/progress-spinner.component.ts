import { ProgressHandlerService } from './../../services/progress-handler/progress-handler.service';
import { Component, OnInit, Inject } from '@angular/core';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { ISpinnerInfo } from 'src/app/interfaces/client/ISpinnerInfo';

@Component({
  selector: 'app-progress-spinner',
  templateUrl: './progress-spinner.component.html',
  styleUrls: ['./progress-spinner.component.scss'],
})
export class ProgressSpinnerComponent implements OnInit {
  constructor(
    public dialogRef: MatDialogRef<ProgressSpinnerComponent>,
    @Inject(MAT_DIALOG_DATA) public spinnerInfo: ISpinnerInfo,
    private progressHandlerService: ProgressHandlerService
  ) {
    this.progressHandlerService.onActionCompleted.subscribe(() => {
      this.dialogRef.close();
    });
  }

  ngOnInit(): void {
    
  }
}
