import os

parcels = open('components/ParcelsTab.tsx', 'r', encoding='utf-8').read()
parcels = parcels.replace('acc.findIndex(item => item.id === curr.id)', 'acc.findIndex((item: Parcel) => item.id === curr.id)')
parcels = parcels.replace('queuedParcels.find(q => q.id === curr.id)', 'queuedParcels.find((q: Parcel) => q.id === curr.id)')
with open('components/ParcelsTab.tsx', 'w', encoding='utf-8') as f:
    f.write(parcels)

print("Done")
