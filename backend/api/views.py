from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from rest_framework import status
from django.db.models import Avg, Count
from .models import Dataset, Equipment
from .serializers import DatasetSerializer, EquipmentSerializer
import pandas as pd
import io

class UploadView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request, format=None):
        if 'file' not in request.data:
            return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)

        file_obj = request.data['file']
        
        if not file_obj.name.endswith('.csv'):
            return Response({'error': 'File must be a CSV'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Read CSV
            df = pd.read_csv(file_obj)
            
            # Simple validation of headers
            required_cols = ['Equipment Name', 'Type', 'Flowrate', 'Pressure', 'Temperature']
            if not all(col in df.columns for col in required_cols):
                 return Response({'error': f'Missing columns. Required: {required_cols}'}, status=status.HTTP_400_BAD_REQUEST)

            # Create Dataset
            dataset = Dataset.objects.create(filename=file_obj.name)

            # Bulk create equipment
            equipment_list = []
            for _, row in df.iterrows():
                equipment_list.append(Equipment(
                    dataset=dataset,
                    name=row['Equipment Name'],
                    type=row['Type'],
                    flowrate=row['Flowrate'],
                    pressure=row['Pressure'],
                    temperature=row['Temperature']
                ))
            
            Equipment.objects.bulk_create(equipment_list)

            return Response({'message': 'Upload successful', 'id': dataset.id}, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def get_dataset_summary(dataset):
    equipment = dataset.equipment.all()
    
    # Calculate stats
    avg_flowrate = equipment.aggregate(Avg('flowrate'))['flowrate__avg'] or 0
    avg_pressure = equipment.aggregate(Avg('pressure'))['pressure__avg'] or 0
    avg_temperature = equipment.aggregate(Avg('temperature'))['temperature__avg'] or 0
    
    # Type distribution
    type_counts = equipment.values('type').annotate(count=Count('type'))
    type_distribution = {item['type']: item['count'] for item in type_counts}

    data = EquipmentSerializer(equipment, many=True).data

    return {
        'id': dataset.id,
        'filename': dataset.filename,
        'upload_date': dataset.upload_date,
        'avg_flowrate': avg_flowrate,
        'avg_pressure': avg_pressure,
        'avg_temperature': avg_temperature,
        'type_distribution': type_distribution,
        'data': data
    }

class SummaryView(APIView):
    def get(self, request):
        latest_dataset = Dataset.objects.order_by('-upload_date').first()
        if not latest_dataset:
             return Response({'error': 'No data available'}, status=status.HTTP_404_NOT_FOUND)
        
        summary = get_dataset_summary(latest_dataset)
        return Response(summary)

from django.contrib.auth.models import User
from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework.serializers import ModelSerializer

class RegisterSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'password', 'email')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(
            validated_data['username'],
            validated_data['email'],
            validated_data['password']
        )
        return user

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

class HistoryView(APIView):
    def get(self, request):
        datasets = Dataset.objects.order_by('-upload_date')[:5]
        # For history, frontend likely expects metadata + maybe summary. 
        # Requirement: "Clicking a history item should load and display... summary, charts, table".
        # So we should probably return full details for each history item or handle it lightly.
        # Frontend code assumes history items have structure similar to summary? 
        # Let's check frontend code assumption.
        # Dashboard.js: `if (item.data && item.type_distribution)` -> Implies full data attached to history item list
        
        response_data = []
        for ds in datasets:
             response_data.append(get_dataset_summary(ds))
        
        return Response(response_data)

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from django.http import HttpResponse
import matplotlib.pyplot as plt
import io

# Set Matplotlib backend to Agg for non-interactive server use
plt.switch_backend('Agg')

def create_pie_chart(data):
    """
    Creates a pie chart for equipment type distribution.
    Returns a BytesIO object containing the chart image.
    """
    labels = list(data.keys())
    sizes = list(data.values())
    
    # Lyna palette
    colors = ['#076653', '#E3EF26', '#0C342C', '#E2FBCE', '#2E8B57', '#9ACD32']
    
    fig, ax = plt.subplots(figsize=(6, 4))
    # Set cream background
    fig.patch.set_facecolor('#FFFDEE')
    ax.set_facecolor('#FFFDEE')
    
    wedges, texts, autotexts = ax.pie(sizes, labels=labels, autopct='%1.1f%%',
                                      startangle=90, colors=colors[:len(labels)],
                                      textprops={'color': "#06231D", 'fontsize': 10})
    
    ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    plt.title("Equipment Type Distribution", color="#076653", fontsize=12, fontweight='bold', pad=12)
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', dpi=100, facecolor='#FFFDEE')
    plt.close(fig)
    buf.seek(0)
    return buf

def create_bar_chart(avg_flow, avg_press, avg_temp):
    """
    Creates a bar chart for average parameters.
    Returns a BytesIO object containing the chart image.
    """
    # Create figure with custom layout and cream background
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8, 4), gridspec_kw={'width_ratios': [2, 1]})
    plt.subplots_adjust(wspace=0.4)
    fig.patch.set_facecolor('#FFFDEE')
    ax1.set_facecolor('#FFFDEE')
    ax2.set_facecolor('#FFFDEE')

    # Subplot 1: Flowrate & Temperature
    params1 = ['Flowrate\n(L/min)', 'Temperature\n(°C)']
    values1 = [avg_flow, avg_temp]
    bars1 = ax1.bar(params1, values1, color='#076653', alpha=0.9, width=0.6)
    
    ax1.set_title('Flow & Temp Averages', color="#076653", fontsize=10, fontweight='bold', pad=12)
    ax1.grid(axis='y', linestyle='--', alpha=0.3)
    ax1.tick_params(axis='x', rotation=0, colors='#0C342C', labelsize=8)
    ax1.tick_params(axis='y', colors='#0C342C', labelsize=8)
    
    # Add values on top
    for bar in bars1:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.1f}',
                ha='center', va='bottom', fontsize=8, color='#06231D', fontweight='bold')

    # Subplot 2: Pressure (separate scale)
    params2 = ['Pressure\n(Bar)']
    values2 = [avg_press]
    bars2 = ax2.bar(params2, values2, color='#E3EF26', alpha=0.9, width=0.6)
    
    ax2.set_title('Avg Pressure', color="#076653", fontsize=10, fontweight='bold', pad=12)
    ax2.grid(axis='y', linestyle='--', alpha=0.3)
    ax2.tick_params(axis='x', colors='#0C342C', labelsize=8)
    ax2.tick_params(axis='y', colors='#0C342C', labelsize=8)

    for bar in bars2:
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.1f}',
                ha='center', va='bottom', fontsize=8, color='#06231D', fontweight='bold')

    # Global styling
    for ax in [ax1, ax2]:
        for spine in ax.spines.values():
            spine.set_edgecolor('#E2FBCE')

    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', dpi=100, facecolor='#FFFDEE')
    plt.close(fig)
    buf.seek(0)
    return buf

class PDFReportView(APIView):
    def get(self, request, pk):
        try:
            dataset = Dataset.objects.get(pk=pk)
            summary = get_dataset_summary(dataset)

            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="report_{dataset.filename}.pdf"'

            doc = SimpleDocTemplate(response, pagesize=letter, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
            styles = getSampleStyleSheet()
            
            # Custom Styles - Lyna Palette
            primary_green = colors.HexColor('#076653') # Deep Green
            secondary_green = colors.HexColor('#0C342C') # Forest Green
            accent_lime = colors.HexColor('#E3EF26') # Lime
            bg_cream = colors.HexColor('#FFFDEE') # Cream
            bg_pale = colors.HexColor('#E2FBCE') # Pale Green
            
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                textColor=primary_green,
                spaceAfter=12,
                fontName='Helvetica-Bold'
            )
            
            subtitle_style = ParagraphStyle(
                'CustomSubtitle',
                parent=styles['Normal'],
                fontSize=12,
                textColor=secondary_green,
                spaceAfter=24
            )

            section_header_style = ParagraphStyle(
                'SectionHeader',
                parent=styles['Heading2'],
                fontSize=16,
                textColor=secondary_green,
                spaceBefore=12,
                spaceAfter=12,
                borderPadding=5,
                borderColor=primary_green,
                borderWidth=0,
                borderBottomWidth=1
            )

            elements = []

            # 1. Header
            elements.append(Paragraph("Chemical Equipment Visualizer", subtitle_style))
            elements.append(Paragraph(f"Analysis Report: {dataset.filename}", title_style))
            elements.append(Paragraph(f"Generated on: {dataset.upload_date.strftime('%Y-%m-%d %H:%M')}", subtitle_style))
            elements.append(Spacer(1, 12))

            # 2. Charts Section
            elements.append(Paragraph("Visual Analysis", section_header_style))
            
            # Generate Charts
            pie_buf = create_pie_chart(summary['type_distribution'])
            bar_buf = create_bar_chart(summary['avg_flowrate'], summary['avg_pressure'], summary['avg_temperature'])
            
            # Add Charts to PDF (Side by Side if possible, or stacked)
            # Stacked is safer for layout
            img_pie = RLImage(pie_buf, width=4*inch, height=2.6*inch)
            img_bar = RLImage(bar_buf, width=5.5*inch, height=2.75*inch)
            
            # Table for visual layout of charts
            chart_table = Table([[img_pie], [img_bar]], colWidths=[6*inch])
            chart_table.setStyle(TableStyle([
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('BOTTOMPADDING', (0,0), (-1,-1), 12),
            ]))
            elements.append(chart_table)
            elements.append(Spacer(1, 12))

            # 3. Summary Statistics Table
            elements.append(Paragraph("Key Metrics", section_header_style))
            stats_data = [
                ['Metric', 'Value'],
                ['Total Equipment Count', f"{len(summary['data'])}"],
                ['Avg Flowrate', f"{summary['avg_flowrate']:.2f}"],
                ['Avg Pressure', f"{summary['avg_pressure']:.2f}"],
                ['Avg Temperature', f"{summary['avg_temperature']:.2f}"]
            ]
            
            t_stats = Table(stats_data, colWidths=[3*inch, 2*inch])
            t_stats.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), primary_green),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
                ('TOPPADDING', (0, 0), (-1, 0), 10),
                ('BACKGROUND', (0, 1), (-1, -1), bg_cream),
                ('GRID', (0, 0), (-1, -1), 1, colors.white),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [bg_cream, bg_pale])
            ]))
            elements.append(t_stats)
            elements.append(Spacer(1, 24))

            # 4. Detailed Data Table (Top 50)
            elements.append(Paragraph("Detailed Equipment Data (Top 50)", section_header_style))
            
            table_header = ['Name', 'Type', 'Flowrate', 'Pressure', 'Temperature']
            table_data = [table_header]
            
            for item in summary['data'][:50]:
                 table_data.append([
                     item['Equipment Name'][:25] + '...' if len(item['Equipment Name']) > 25 else item['Equipment Name'], 
                     item['Type'], 
                     f"{item['Flowrate']:.1f}", 
                     f"{item['Pressure']:.1f}", 
                     f"{item['Temperature']:.1f}"
                 ])
            
            t_data = Table(table_data, colWidths=[2.5*inch, 1.2*inch, 0.9*inch, 0.9*inch, 1*inch], repeatRows=1)
            t_data.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), primary_green),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                ('TOPPADDING', (0, 0), (-1, 0), 8),
                ('GRID', (0, 0), (-1, -1), 0.5, bg_pale),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [bg_cream, bg_pale]),
                ('ALIGN', (2, 1), (-1, -1), 'RIGHT'), # Align numbers to right
            ]))
            elements.append(t_data)

            # Build PDF
            doc.build(elements)
            return response
            
        except Dataset.DoesNotExist:
            return Response({'error': 'Dataset not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            # Important: Print error to console for debugging since PDF generation errors can be silent
            print(f"PDF Generation Error: {str(e)}")
            import traceback
            traceback.print_exc()
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
