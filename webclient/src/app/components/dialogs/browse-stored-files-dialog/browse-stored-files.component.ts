import { Component, OnInit, Inject } from '@angular/core';
import {
  MatDialogRef,
  MAT_DIALOG_DATA,
  MatDialog,
} from '@angular/material/dialog';
import { ProgressHandlerService } from 'src/app/services/progress-handler/progress-handler.service';
import { S3Service } from 'src/app/services/s3/s3.service';
import { ProgressSpinnerComponent } from '../../progress-spinner/progress-spinner.component';
@Component({
  selector: 'app-browse-stored-files',
  templateUrl: './browse-stored-files.component.html',
  styleUrls: ['./browse-stored-files.component.scss'],
})
export class BrowseStoredFilesComponent implements OnInit {
  loaded = false;
  constructor(
    private s3Service: S3Service,
    public dialogRef: MatDialogRef<BrowseStoredFilesComponent>,
    @Inject(MAT_DIALOG_DATA) public fileList: string[],
    public dialog: MatDialog,
    private progressHandlerService: ProgressHandlerService
  ) {}

  ngOnInit(): void {}

  async load(file: string) {
    this.dialog.open(ProgressSpinnerComponent, {
      data: {
        header: 'Downlading File',
        subheader: 'Downlaoding & loading selected file',
      },
      disableClose: true,
    });
    const result = await this.s3Service.loadDeploymentFile(file);
    this.progressHandlerService.onActionCompleted.next(true);
    this.dialogRef.close({ loaded: true, loadedForm: result });
  }
}
